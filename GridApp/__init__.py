#!/usr/bin/env python
import os
from flask import Flask, render_template, session, request, make_response
import uuid

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
        n = _n
        m = _m
        seed = _seed 
        self.user = _user

processing_users = set()
task_queue = list()
completed_tasks = list()
running_taks = list()

@APP.route('/', methods=["GET", "POST"])
def index():
    user_id = request.cookies.get('user_id')
    if not user_id:
        user_id = uuid.uuid4()
        state = "send task"
    elif len(filter(lambda x: x if x.user == user_id else None, task_queue)) != 0:
        state = "your task is already in queue"
    elif len(filter(lambda x: x if x.user == user_id else None, processing_users)) != 0:
        state = "your task is processing"
    elif len(filter(lambda x: x if x.user == user_id else None, completed_tasks)) != 0:
        pass
    else:
        if request.method == "POST":
            state = "your task accepted"
            new_task = task(request.form["nodes"], request.form["edges"], request.form["seed"], user_id)
            task_queue.append(new_task)
        else:
            state = "send task"
    resp = make_response(render_template('index.html', state = state))
    resp.set_cookie("user_id", bytes(user_id))
    return resp


if __name__ == '__main__':
    APP.debug=True
    APP.run()