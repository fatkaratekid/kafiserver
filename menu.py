from urllib import request
from bs4 import BeautifulSoup as soup
from urllib.parse import urljoin
from datetime import date
from pdf2text import convert_pdf_to_text
import tempfile
import re
import redis
import os
from urllib.error import HTTPError
import sys


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
    try:
        req = request.urlopen(base_url)
    except HTTPError:
        return None
    if req.code == 200:
        return req.read()
    raise ValueError('Error {0}'.format(req.status_code))


def get_all_links(html):
    bs = soup(html)
    links = bs.findAll('a')
    return links


def _is_menu_file(link, current_week):
    file_name = link.rsplit('/', 1)[-1]

    print('link: ', link, file=sys.stdout)
    sys.stdout.flush()

    return (
            link[-4:] == '.pdf'
            and str(current_week) in file_name
            and '_menu' in file_name.lower()
    )


def get_image(image_description):
    raise NotImplementedError


def check_redis_conenction():
    try:
        r.ping()
    except redis.ConnectionError:
        init_redis()


def set_menus_from_db(menus_key, menus_today):
    check_redis_conenction()
    return r.set(menus_key, menus_today)


def get_menus_from_db(menus_key):
    check_redis_conenction()
    menus_raw = r.get(menus_key)
    if menus_raw is None:
        return None
    return eval(menus_raw)


def get_pattern_text_to_menus():
    re1 = '((?:Montag|Dienstag|Mittwoch|Donnerstag|Freitag))'  # Day Of Week 1
    re2 = '.*?'  # Non-greedy match on filler
    re3 = '((?:Jan(?:uar)?|Feb(?:ruar)?|Mär(?:z)?|Apr(?:il)?|Mai|Jun(?:i)?|Jul(?:i)?|Aug(?:ust)?|Sep(?:tember)?|Sept|Okt(?:ober)?|Nov(?:ember)?|Dez(?:ember)?))'  # Month 1
    re4 = '.*?'  # Non-greedy match on filler
    re5 = '20[0-9]{2}'  # Year 1

    return re.compile(re1 + re4 + re5, re.IGNORECASE)


def get_menus(base_url, menu_format='text'):

    current_week = date.today().isocalendar()[1]
    current_day_idx = date.today().weekday()

    menus_key = '{}_{}'.format(current_week, current_day_idx)

    if menu_format == 'text':
        menus_today = get_menus_from_db(menus_key)
        if menus_today is not None:
            return menus_today

    html = get_page(base_url)
    if html is None:
        return [['menu page does not exist']]
    links = get_all_links(html)
    if len(links) == 0:
        return [['no menu PDF links found on the menu page']]

    regex_menu_type = re.compile('Woche [0-9]+')
    regex_day = re.compile(
        '[A-Z]{1}[a-z]+,[ ]*[0-9]{2}.[ ]*[A-Z]{1}[äa-z]+ 20[0-9]{2}'
    )
    # regex_day = get_pattern_text_to_menus()

    menu_links = [
        l for l in links
        if _is_menu_file(l['href'], current_week)
    ]

    if menu_format == 'url':
        return [menu_links]

    menus_today = []
    for link in menu_links:
        print('openming url', urljoin(base_url, link['href']))
        content = request.urlopen(urljoin(base_url, link['href']))
        content_type = content.headers['content-type']
        is_pdf = (
                content.status == 200
                and content_type == 'application/pdf'
        )

        print(is_pdf, file=sys.stdout)
        sys.stdout.flush()

        if is_pdf:
            print('it is pdf, we are parsing now', is_pdf, file=sys.stdout)
            sys.stdout.flush()

            with tempfile.NamedTemporaryFile() as f:
                f.write(content.read())
                text = convert_pdf_to_text(f.name).strip()

            text = re.sub('[^A-Za-z0-9 \nöäüéàè&ÖÄÜÉÀÈ\-,.!?_\'"|]+', '', text)

            print('here is text: ', text, file=sys.stdout)
            sys.stdout.flush()

            menus_on_pdf = regex_menu_type.split(text)[1:]

            menus_today.extend(
                [
                    regex_day.split(
                        repr(m.strip())
                    )[current_day_idx+1]
                    .replace('\\n', '')
                    .split('|')
                    for m in menus_on_pdf
                ]
            )
    if not menus_today:
        return [['none of the PDFs contain correct info or no correct PDFs found']]

    set_menus_from_db(menus_key, menus_today)

    return menus_today

