# Third Huge Freckled Elephant
# Ethan Shenker, Constance Chen, Andrew Jiang, Saqif Abedin
# P0 - To Be Named
# 2020-12-xx

from flask import Flask, render_template, session, request
from uuid import uuid4      # how to get unique user_id strings
from helpers import a_clean # function I defined in helpers.py file
import datetime             # how to get current date / time
import sqlite3
import os
import sys ## we won't need this

app = Flask(__name__)
app.secret_key = os.urandom(32)


@app.route("/")
def root():
    return landing()

@app.route("/fake_auth")
def fake_auth():
    session['user_id'] = int(request.args['user_id'])
    return root()

@app.route("/logout")
def logout():
    if session.get('user_id'):
        session.pop('user_id')  
    return root()
    
@app.route("/home")
def landing():
    if session.get('user_id'):
        return user_page()
    return render_template("launch.html")

@app.route("/test")
def test():
    return render_template("test.html")

## Route that provides feed -- not pretty at all, simply post entries in raw form
@app.route("/feed")
def feed():
    ## TODO have the feed based on the users that the person logged in is following
    db = sqlite3.connect("blog.db")
    c = db.cursor()
    posts = c.execute("SELECT * FROM posts ORDER BY post_date DESC").fetchall()
    return render_template("feed.html", posts=posts)

## Unnecessary (will be taken out), but section found on create_post.html 
## should go wherever that functionality ends up
@app.route("/create_post")
def create_post():
    return render_template("create_post.html")

@app.route("/action_create_post")
def action_create_post():
    db = sqlite3.connect("blog.db")
    c = db.cursor()
    user_id = session.get('user_id')
    post_id = uuid4() ## random 32-bit ID number
    post_date = str(datetime.datetime.now())[:19] ## "yyyy-mm-dd hh:mm:ss"
    post_title = request.args['post_title']
    post_content = request.args['post_content'].strip()
    query = f"INSERT INTO posts VALUES ({user_id}, '{post_id}', '{post_date}', '{a_clean(post_title)}', '{a_clean(post_content)}')"
    c.execute(query)
    db.commit() 
    db.close()
    return render_template("launch.html")

@app.route("/user_page")
def user_page():
    user_id = session.get("user_id") ## TODO make home page work only if someone is logged in
    db = sqlite3.connect("blog.db")
    c = db.cursor()
    query = f"SELECT * FROM posts WHERE user_id={user_id}"
    posts = c.execute(query).fetchall()
    db.close()
    return render_template("user_page.html", posts=posts) # user=username)


if __name__ == '__main__':
    app.debug = True
    app.run()
    