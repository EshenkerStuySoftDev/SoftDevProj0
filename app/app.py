# Third Huge Freckled Elephant
# Ethan Shenker, Constance Chen, Andrew Jiang, Saqif Abedin
# P0 - To Be Named
# 2020-12-xx

from flask import Flask, render_template, session, request
from uuid import uuid4      # how to get unique user_id strings
from helpers import a_clean, tup_clean, check_blog_conflicts
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
    print("feed")
    return permissions()


# ------------------------------------------------------------------------------
# Section for creating a blog

@app.route("/create_blog")
def create_blog():
    if session.get("user_id"):
        return render_template("create_blog.html")
    print("create blog")
    return permissions()


@app.route("/action_create_blog")
def action_create_blog(name=None, content=None, title=None):
    if session.get("user_id"):
        db = sqlite3.connect("blog.db")
        c = db.cursor()

        user_id = session.get('user_id')
        blog_id = uuid4()
        post_date = str(datetime.datetime.now())[:19]

        if name:
            blog_name = a_clean(name.title())
        else:
            blog_name = a_clean(request.args['blog_name']).title()
            print(blog_name)

        # Ensures that no two blogs by the same user have the same blog_id
        while True:
            query = f"SELECT * FROM blogs WHERE user_id='{user_id}' AND blog_id='{blog_id}'"
            c.execute(query)
            conflicts = list(c)
            if len(conflicts) > 0:
                blog_id = uuid4()
            else:
                break

        
        if check_blog_conflicts(user_id, blog_name):
            if name:
                return render_template("create_post.html", error=True, new_blog=True, post_content=content, post_title=title)
            else:
                return render_template("create_blog.html", error=True)


        query = f"INSERT INTO blogs VALUES ('{user_id}', '{blog_id}', '{blog_name}', '{post_date}')"
        print(query)

        c.execute(query)
        db.commit() 
        db.close()
        return user_page()
    return permissions()



# ------------------------------------------------------------------------------
# Section for creating a post

## Unnecessary route (will be taken out), but section found on create_post.html 
## should go wherever that functionality ends up
@app.route("/create_post")
def create_post(new_blog=False, content=None, title=None):
    if session.get("user_id"):
        db = sqlite3.connect("blog.db")
        c = db.cursor()
        user_id = session.get("user_id")
        query = f"SELECT blog_name FROM blogs WHERE user_id='{user_id}'"
        c.execute(query)
        blogs = tup_clean(list(c))
        if not new_blog:
            blogs.append("New Blog")
        db.close()
        if content:
            return render_template("create_post.html", new_blog=True, post_title=title, post_content=content)
        else:
            return render_template("create_post.html", blogs=blogs)
    return permissions()


@app.route("/action_create_post")
def action_create_post():
    if session.get("user_id"):
        post_title = request.args['post_title']
        post_content = request.args['post_content']

        try:
            blog_name = a_clean(request.args['new_blog_title']).title()
            action_create_blog(blog_name, content=post_content, title=post_title) # maybe include a return statement
        except KeyError:
            blog_name = a_clean(request.args['blog_title']).title()
            if blog_name == "New Blog":
                return create_post(new_blog=True, content=post_content, title=post_title)

        db = sqlite3.connect("blog.db")
        c = db.cursor()
        user_id, post_id, post_date = session.get('user_id'), uuid4(), str(datetime.datetime.now())[:19]
        post_title, post_content = a_clean(post_title), a_clean(post_content.strip())


        query = f"SELECT blog_id FROM blogs WHERE blog_name='{blog_name}'"
        print(query)
        c.execute(query)
        blog_id = tup_clean(list(c))[0]

        query = f"INSERT INTO posts VALUES ('{user_id}', '{blog_id}', '{post_id}', '{post_date}', '{post_title}', '{post_content}')"
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
        query = f"SELECT * FROM blogs WHERE user_id={user_id} ORDER BY post_date DESC"
        c.execute(query)
        blogs = list(c)
        db.close()
        return render_template("user_page.html", blogs=blogs) # user=username)
    print("user page")
    return permissions()


# ------------------------------------------------------------------------------
# Section for user's personal pages

@app.route("/blog_page")
def blog_page():
    if session.get("user_id"):
        user_id = session.get("user_id")
        blog_id = request.args['blog_id']

        db = sqlite3.connect("blog.db")
        c = db.cursor()

        query = f"SELECT blog_name FROM blogs where user_id='{user_id}' AND blog_id='{blog_id}'"
        c.execute(query)
        blog_name = tup_clean(list(c))[0]
        print(blog_name)

        query = f"SELECT * FROM posts WHERE user_id='{user_id}' AND blog_id='{blog_id}'"
        c.execute(query)
        posts = list(c)

        return render_template("blog_page.html", posts=posts, blog_name=blog_name)
    return permissions()

    
# ------------------------------------------------------------------------------

if __name__ == '__main__':
    app.debug = True
    app.run()
    