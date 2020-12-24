# Third Huge Freckled Elephant
# Ethan Shenker, Constance Chen, Andrew Jiang, Saqif Abedin
# P0 - To Be Named
# 2020-12-xx

from flask import Flask, render_template, session, request
import sqlite3
from uuid import uuid4
import os
import sys

app = Flask(__name__)
app.secret_key = os.urandom(32)

@app.route("/")
def landing():
    return render_template("launch.html")

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/create_post")
def create_post():
    return render_template("create_post.html")

@app.route("/action_create_post")
def action_create_post():

    try:
        ## user_id will be dependent on the session but users need to be created before
        ## that can be implemented
        ## post_id can either be a unique number (uuid module) or some other way we track the variable
        ## post date--we can import date module to work with that or we can come up with some arbitrary
        ## tracking system

        db = sqlite3.connect("blog.db")
        c = db.cursor()

        '''
        user_id = 1
        post_date = "now"
        '''
        # user_id = ## user_id
        # post_date = ## some time method


        post_title = request.args['post_title']
        post_content = request.args['post_content']
        post_id = uuid4() ## random 32-bit ID number

        query = f"INSERT INTO posts VALUES ({user_id}, '{post_id}', '{post_date}', '{post_title}', '{post_content}');"
        c.execute(query)
        
        db.commit() 
        db.close()
        
        return render_template("success.html")
    
    except:
        return render_template("error.html", error=sys.exc_info()[0])

if __name__ == '__main__':
    app.debug = True
    app.run()
    