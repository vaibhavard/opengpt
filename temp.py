from flask import Flask, session
from flask_session import Session
from helpers import helper
import json
app = Flask(__name__)
# Check Configuration section for more details
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)


@app.route('/')
def reset():
    session["counter"]=0
    return 'data: %s\n\n' % json.dumps(helper.streamer("counter was reset"), separators=(',' ':'))

@app.route("/v1/models")
def models():
    print("Models")
    return helper.model

@app.route("/v1/chat/completions", methods=['POST'])
def routeA():
    if not "counter" in session:
        session["counter"]=0

    session["counter"]+=1
    return 'data: %s\n\n' % json.dumps(helper.streamer("counter is {}".format(session["counter"])), separators=(',' ':'))


@app.route('/dec')
def routeB():
    if not "counter" in session:
        session["counter"] = 0

    session["counter"] -= 1

    return "counter is {}".format(session["counter"])

