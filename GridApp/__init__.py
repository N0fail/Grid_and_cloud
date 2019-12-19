#!/usr/bin/env python
import os
from flask import Flask, render_template, session, request, make_response
import uuid
import broker
import threading
from flask import url_for

# Create the application.
APP = Flask(__name__)
APP.config.update(
    #Set the secret key to a sufficiently random value
    SECRET_KEY=os.urandom(24),

    #Set the session cookie to be secure
    SESSION_COOKIE_SECURE=True,

    #Set the session cookie for our app to a unique name
    SESSION_COOKIE_NAME="session",
    
    WTF_CSRF_TIME_LIMIT=None

)
class task:
    #n = 2
    #m = 1
    #seed = 1
    user = None
    def __init__(self, _n, _m, _seed, _user):
        self.n = _n
        self.m = _m
        self.seed = _seed 
        self.user = _user

queue_tasks = list()
running_tasks = set()
completed_tasks = set()

threading.Thread(target=broker.main, args=(queue_tasks, running_tasks, completed_tasks)).start()  # run broker process in background

@APP.route('/', methods=["GET", "POST"])
def index():
    user_id = request.cookies.get('user_id')
    pic = "wait.jpg"
    if not user_id:
        user_id = uuid.uuid4()
        state = "send task"
    elif user_id in set(map(lambda x: x.user, queue_tasks)):
        state = "your task is already in queue"
    elif user_id in set(map(lambda x: x.user, running_tasks)):
        state = "your task is processing"
    elif user_id in set(map(lambda x: x.user, completed_tasks)):
        for i in completed_tasks:
            if i.user == user_id:
                elem = i
                break
        completed_tasks.discard(elem)
        state = "send task"
        pic = "{}_{}_{}.png".format(elem.n, elem.m, elem.seed)
        # todo: send results
        pass
    else:
        if request.method == "POST":
            state = "your task accepted"
            new_task = task(request.form["nodes"], request.form["edges"], request.form["seed"], user_id)
            queue_tasks.append(new_task)
        else:
            state = "send task"
    resp = make_response(render_template('index.html', state = state, picture=pic))
    resp.set_cookie("user_id", str(user_id))
    return resp


if __name__ == '__main__':
    APP.debug=True
    APP.run()
