# Third Huge Freckled Elephant
# Ethan Shenker, Constance Chen, Andrew Jiang, Saqif Abedin
# P0 - To Be Named
# 2020-12-xx

from flask import Flask, render_template, session, request
from uuid import uuid4      # how to get unique user_id strings
import datetime             # how to get current date / time
import sqlite3
import os
import sys ## we won't need this #TODO remove

app = Flask(__name__)
app.secret_key = os.urandom(32)


@app.route("/home")
def landing():
    if session.get('user_id'):
        return user_page()
    return render_template("launch.html")


@app.route("/")
def root():
    return landing()


# Function if user tries to access user-only content while not logged in
def permissions():
    return render_template("permissions.html")


# ------------------------------------------------------------------------------
# Section for Authentication

@app.route("/fake_auth")
def fake_auth():
    session['user_id'] = int(request.args['user_id'])
    return root()


@app.route("/logout")
def logout():
    if session.get('user_id'):
        session.pop('user_id')  
    return root()


# ------------------------------------------------------------------------------
# Section for Feed

@app.route("/feed")
def feed():
    if session.get("user_id"):
        ## TODO have the feed based on the users that the person logged in is following
        db = sqlite3.connect("blog.db")
        c = db.cursor()
        c.execute("SELECT * FROM posts ORDER BY post_date DESC")
        posts = list(c)
        return render_template("feed.html", posts=posts)
    return permissions()


# ------------------------------------------------------------------------------
# Section for creating a post

## Unnecessary route (will be taken out), but section found on create_post.html 
## should go wherever that functionality ends up
@app.route("/create_post")
def create_post():
    if session.get("user_id"):
        return render_template("create_post.html")
    return permissions()


def a_clean(string):
    output = ""
    for char in string:
        if char == "'":
            output += "'"
        output += char
    return output


@app.route("/action_create_post")
def action_create_post():
    if session.get("user_id"):
        db = sqlite3.connect("blog.db")
        c = db.cursor()
        user_id, post_id, post_date = session.get('user_id'), uuid4(), str(datetime.datetime.now())[:19]
        post_title, post_content = a_clean(request.args['post_title']), a_clean(request.args['post_content'].strip())
        query = f"INSERT INTO posts VALUES ({user_id}, '{post_id}', '{post_date}', '{post_title}', '{post_content}')"
        c.execute(query)
        db.commit() 
        db.close()
        return user_page()
    return permissions()
    

# ------------------------------------------------------------------------------
# Section for user's personal pages

@app.route("/user_page")
def user_page():
    if session.get("user_id"):
        user_id = session.get("user_id") ## TODO make home page work only if someone is logged in
        db = sqlite3.connect("blog.db")
        c = db.cursor()
        query = f"SELECT * FROM posts WHERE user_id={user_id} ORDER BY post_date DESC"
        c.execute(query)
        posts = list(c)
        db.close()
        return render_template("user_page.html", posts=posts) # user=username)
    return permissions()


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    app.debug = True
    app.run()
    