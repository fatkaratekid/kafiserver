import pusher
import os
from flask import Flask, url_for

app = Flask(__name__)
print(app)

pusher_client = None
print(os.environ)

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


@app.route('/')
def api_root():
    menu = 'Hoi! Kafi Server hier ^_^. Es ist schön ois kanne z\'lärne.'
    menu +='<br><br><a href="/want">Say you that you want Kafi!</a>'
    menu +='<br><br><a href="/brewing">Kafi is brewing...</a>'
    menu +='<br><br><a href="/done">Say that you made Kafi! (good guy you)</a>'
    menu += '<br><br>'
    return menu,200

@app.route('/desire')
@app.route('/want')
def desire():
    print('triggered desire')
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
    return 'Done - sent',200


if __name__ == '__main__':
    print('Running server now')
    init()
    app.run()
