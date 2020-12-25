# Third Huge Freckled Elephant
# Ethan Shenker, Constance Chen, Andrew Jiang, Saqif Abedin
# P0 - To Be Named
# 2020-12-xx

from flask import Flask, render_template, session, request
from uuid import uuid4
from helpers import clean_apostrophes as a_clean
import datetime
import sqlite3
import os
import sys ## we won't need this

app = Flask(__name__)
app.secret_key = os.urandom(32)

@app.route("/")
def landing():
    return render_template("launch.html")

@app.route("/test")
def test():
    return render_template("test.html")


## Route that provides feed -- not pretty at all, simply post objects in raw form
@app.route("/feed")
def feed():
    db = sqlite3.connect("blog.db")
    c = db.cursor()
    c.execute("SELECT * FROM posts ORDER BY post_date DESC") ## TODO come up with sorting mechanism
    posts = list(c)
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
    # user_id = session.get('user_id') ## TODO once user is logged in, assign post user_id from session profile @andrew
    user_id = 1
    post_id = uuid4() ## random 32-bit ID number
    post_date = str(datetime.datetime.now())[:19] ## "yyyy-mm-dd hh:mm:ss"
    post_title = a_clean(request.args['post_title']) ## data from form
    post_content = a_clean(request.args['post_content'].strip())

    print(post_title)
    print(post_content)
    ## TODO fix error here b/c query won't accept text with single-quotes in it
    query = f"INSERT INTO posts VALUES ({user_id}, '{post_id}', '{post_date}', '{post_title}', '{post_content}')"
    c.execute(query)
    db.commit() 
    db.close()

    return render_template("launch.html")


if __name__ == '__main__':
    app.debug = True
    app.run()
    