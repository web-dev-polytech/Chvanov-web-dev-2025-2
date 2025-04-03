import os
from flask import Flask, render_template, session, abort, make_response, request, redirect, url_for
from flask_login import Login


app = Flask(__name__)
application = app

app.secret_key = os.environ.get('SECRET_KEY')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/counter')
def counter():
    if session.get('counter'):
        session['counter'] += 1
    else:
        session['counter'] = 1
    return render_template('counter.html')

@app.route('/auth')
def auth():
    return render_template('auth.html')