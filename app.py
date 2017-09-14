import pusher
import os
from flask import Flask, url_for

app = Flask(__name__)

pusher_client = None

def init():
    global pusher_client
    pusher_client = pusher.Pusher(
      app_id=os.environ["PUSHER_APP_ID"],
      key=os.environ["PUSHER_APP_KEY"],
      secret=os.environ["PUSHER_SECRET"],
      cluster=os.environ["PUSHER_CLUSTER"],
      ssl=True
    )


def push_message(message):
    global pusher_client
    init()
    pusher_client.trigger('kafi-channel', 'kafi-event', {'message': message})


def nchar(n, c='&nbsp;'):
    return n*c


@app.route('/')
def api_root():
    menu  = '<p>'+nchar(17)+ nchar(31,'_')+ '<br>'
    menu += nchar(15)+     '| Hoi! Kafi Server hier.' + nchar(15) + '|<br>'
    menu += nchar(15)+     '| Es ist schön ois kanne z\'lärne. |<br>'
    menu += nchar(15)+     '/   /``````````````````````````````<br>'
    menu += nchar(13) +    '/ /<br>'
    menu += nchar(12) +   '//<br>'
    menu += nchar(8)  +'__/<br>'
    menu += '^_^ ```<br><br><br><br></p>'
    menu += '<p>How do you answer:'
    menu += '<br><br><a href="/want">I want Kafi!</a>'
    menu += '<br><br><a href="/brewing">Kafi is brewing...</a>'
    menu += '<br><br><a href="/done">I "maked" Kafi! (good guy you)</a>'
    menu += '<br><br><a href="/merci">Sag merci</a>'
    menu += '</p>'
    return menu,200


@app.route('/desire')
@app.route('/want')
def desire():
    push_message('Ich will Kafi')
    return 'Longing for coffee - sent',200


@app.route('/cooking')
@app.route('/brewing')
@app.route('/making')
def cooking():
    push_message('Ich mache de Kafi parat')
    return 'I am cooking it - sent',200


@app.route('/done')
@app.route('/bereit')
@app.route('/ready')
@app.route('/parat')
@app.route('/fertig')
@app.route('/ping')
def done():
    push_message('De Kafi isch parat')
    return 'Kafi is ready - sent',200


@app.route('/merci')
@app.route('/danke')
@app.route('/thanks')
def merci():
    push_message('Merci')
    return 'Merci - sent',200


from flask import request
from flask import jsonify
@app.route("/ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200


if __name__ == '__main__':
    print('Running server now')
    init()
    app.run()
