# Third Huge Freckled Elephant
# Ethan Shenker, Constance Chen, Andrew Jiang, Saqif Abedin
# P0 - To Be Named
# 2020-12-xx

from flask import Flask, render_template, session, request
from uuid import uuid4
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
    try:
        db = sqlite3.connect("blog.db")
        c = db.cursor()
        # user_id = session.get('user_id') ## TODO once user is logged in, assign post user_id from session profile @andrew
        user_id = 1
        post_id = uuid4() ## random 32-bit ID number
        post_date = datetime.datetime.now() ## "yyyy-mm-dd hh:mm:ss.xxxxxx"
        post_title = request.args['post_title'] ## data from form
        post_content = request.args['post_content']
    
        query = f"INSERT INTO posts VALUES ({user_id}, '{post_id}', '{post_date}', '{post_title}', '{post_content}');"
        c.execute(query)
        db.commit() 
        db.close()
        return render_template("launch.html")

    except:
        return render_template("error.html", error=sys.exc_info()[0]) ## TODO catch edge cases so we can take out try/catch loop


if __name__ == '__main__':
    app.debug = True
    app.run()
    