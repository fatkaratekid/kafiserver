import pusher
import os
from flask import Flask, url_for, render_template

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


@app.route('/')
def api_root():
    return render_template('layout.html'),200


@app.route('/desire')
@app.route('/want')
def desire():
    push_message('Ich will Kafi')
    return render_template('redirector.html', message='Longing for coffee')


@app.route('/cooking')
@app.route('/brewing')
@app.route('/making')
def cooking():
    push_message('Ich mache de Kafi parat')
    return render_template('redirector.html', message='I am cooking it')


@app.route('/done')
@app.route('/bereit')
@app.route('/ready')
@app.route('/parat')
@app.route('/fertig')
@app.route('/ping')
def done():
    push_message('De Kafi isch parat')
    return render_template('redirector.html', message='Kafi is ready')


@app.route('/merci')
@app.route('/danke')
@app.route('/thanks')
def merci():
    push_message('Merci')
    return render_template('redirector.html', message='merci')


from flask import request
from flask import jsonify
@app.route("/ip", methods=["GET"])
def get_my_ip():
    return jsonify({'ip': request.remote_addr}), 200


if __name__ == '__main__':
    print('Running server now')
    init()
    app.run()
