from urllib import request
from bs4 import BeautifulSoup as soup
from urllib.parse import urljoin
from datetime import date
from pdf2text import convert_pdf_to_txt
import tempfile
import re
import redis
import os


def init_redis():
    global r
    r = redis.Redis.from_url(
        redis_url,
        charset="utf-8",
        decode_responses=True
    )


r = None
redis_url = os.environ['REDIS_URL']
init_redis()


def get_page(base_url):
    req = request.urlopen(base_url)
    if req.code == 200:
        return req.read()
    raise Exception('Error {0}'.format(req.status_code))


def get_all_links(html):
    bs = soup(html)
    links = bs.findAll('a')
    return links


def _is_menu_file(link, current_week):
    file_name = link.rsplit('/', 1)[-1]
    return (
            link[-4:] == '.pdf'
            and 'centro_menues' in link.lower()
            and str(current_week) in file_name
            and 'menu' in file_name.lower()
    )


def get_image(image_description):
    raise NotImplementedError


def check_redis_conenction():
    try:
        r.ping()
    except redis.ConnectionError:
        init_redis()


def set_menus_from_db(menus_key, menus_today):
    try:
        return r.set(menus_key, menus_today)
    except:
        check_redis_conenction()
        return r.set(menus_key, menus_today)


def get_menus_from_db(menus_key):
    try:
        return eval(r.get(menus_key))
    except:
        check_redis_conenction()
        return eval(r.get(menus_key))


def get_menus(base_url):

    current_week = date.today().isocalendar()[1]
    current_day_idx = date.today().weekday()

    menus_key = '{}_{}'.format(current_week, current_day_idx)

    menus_today = get_menus_from_db(menus_key)

    if menus_today:
        return menus_today

    html = get_page(base_url)
    links = get_all_links(html)
    if len(links) == 0:
        raise Exception('No links found on the webpage')

    regex_menu_type = re.compile('Woche [0-9]+')
    regex_day = re.compile(
        '[A-Z]{1}[a-z]+, [0-9]{2}\. [A-Z]{1}[a-z]+ 20[0-9]{2}'
    )

    menus_today = []
    for link in links:
        if not _is_menu_file(link['href'], current_week):
            continue

        content = request.urlopen(urljoin(base_url, link['href']))
        content_type = content.headers['content-type']
        is_pdf = (
                content.status == 200
                and content_type == 'application/pdf'
        )

        if is_pdf:
            with tempfile.NamedTemporaryFile() as f:
                f.write(content.read())
                text = convert_pdf_to_txt(f.name)

            menus_on_pdf = regex_menu_type.split(text)[1:]

            menus_today.extend(
                [
                    regex_day.split(repr(m))[current_day_idx+1]
                    .replace('\\n', '')
                    .split('|')
                    for m in menus_on_pdf
                ]
            )
    if not menus_today:
        raise Exception('No pdfs found on the page')

    set_menus_from_db(menus_key, menus_today)

    return menus_today
