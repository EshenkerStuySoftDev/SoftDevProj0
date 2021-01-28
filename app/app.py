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
sys.path.append("/var/www/SoftDevProj0/app/")


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
# Section for Account Creation / Authentication
@app.route("/register", methods=["POST"]) #post method needed for security
def register():
    # try:
    db = sqlite3.connect("blog.db")#connects to sq
    u = db.cursor()

    password = request.form["password"]
    username = request.form["username"]
    
    if request.form["type"] == "Login":
        u.execute(f"SELECT password, user_id FROM users WHERE username = '{username}'")
        db_pass = list(u) #returns tuple
        if len(db_pass) != 1:
            return render_template("launch.html", usererror=True)
        elif password != db_pass[0][0]:
            return render_template("launch.html", passerror=True)#return bad pass
        else:
            session['username'] = str(request.form['username'])
            session['user_id'] = db_pass[0][1]
            return root()
    elif request.form["type"] == "Sign Up":
        u.execute("SELECT username FROM users")
        check = list(u)
        if (username,) in check:
            return render_template("create_account.html", error=True)
        else:
            user_id = uuid4()
            u.execute(f"INSERT INTO users(user_id, username, password) VALUES ('{user_id}','{username}','{password}')")
            session['username'] = str(username)
            session['user_id'] = user_id
            db.commit()
            return root()
        db.commit()
    return root()
    # except:
    #     return render_template("error.html")
    

@app.route('/create_account')
def create_account():
    return render_template("create_account.html")


@app.route("/logout")
def logout():
    try:    
        if session.get('user_id'): # if user logged in 
            session.pop('user_id') # clear all
            session.pop('username')
        return root()
    except:
        return render_template("error.html")

# ------------------------------------------------------------------------------
# Section for Feed

@app.route("/feed")
def feed():
    try:
        if session.get("user_id"):
            db = sqlite3.connect("blog.db")
            c = db.cursor()
            c.execute("SELECT * FROM posts ORDER BY post_date DESC")
            posts = list(c)
            return render_template("feed.html", posts=posts)
        return permissions()
    except:
        return render_template("error.html")

# ------------------------------------------------------------------------------
# Section for creating a post

@app.route("/create_post")
def create_post(new_blog=False, content=None, title=None):
    try:
        if session.get("user_id"):
            db = sqlite3.connect("blog.db")
            c = db.cursor()
            user_id = session.get("user_id")
            query = f"SELECT blog_name FROM blogs WHERE user_id='{user_id}'"
            c.execute(query)
            blogs = tup_clean(list(c))

            # if a new blog isn't already in the process of being created, give user an extra option
            if not new_blog: 
                blogs.append("New Blog") # adds "new blog" option to blog dropdown menu when creating post

            db.close()

            if content: # stage at which the user is prompted to enter a new blog title
                return render_template("create_post.html", new_blog=True, post_title=title, post_content=content) # only title is new
            else:
                return render_template("create_post.html", blogs=blogs) # standard template
        return permissions()
    except:
        return render_template("error.html")


@app.route("/action_create_post", methods=["POST"])
def action_create_post():
    try:
        if session.get("user_id"):
            post_title = request.form['post_title']
            post_content = request.form['post_content']

            # try to get the field where the user assumedly input the new name of
            # a blog they're looking to create.
            try:
                blog_name = a_clean(request.form['new_blog_title']).title()
                action_create_blog(blog_name, content=post_content, title=post_title) # create that blog
            # if they aren't creating a new blog in that moment, create a post and assign
            # it to the blog they've selected
            except KeyError:
                blog_name = a_clean(request.form['blog_title']).title()
                if blog_name == "New Blog":
                    return create_post(new_blog=True, content=post_content, title=post_title)

            db = sqlite3.connect("blog.db")
            c = db.cursor()
            user_id, username, post_id = session.get('user_id'), session.get('username'), uuid4()
            post_title, post_content = a_clean(post_title), a_clean(post_content.strip())
            post_date = str(datetime.datetime.now())[:19]

            query = f"SELECT blog_id FROM blogs WHERE blog_name='{blog_name}'"
            c.execute(query)
            blog_id = tup_clean(list(c))[0]

            query = f"INSERT INTO posts VALUES ('{user_id}', '{username}', '{blog_id}', '{post_id}', '{post_date}', '{post_title}', '{post_content}')"
            c.execute(query)
            db.commit() 
            db.close()
            return user_page()
        return permissions()
    except:
        return render_template("error.html")

# ------------------------------------------------------------------------------
# Section for creating a blog

@app.route("/create_blog")
def create_blog():
    if session.get("user_id"):
        return render_template("create_blog.html")
    return permissions()


@app.route("/action_create_blog", methods=["POST"])
def action_create_blog(name=None, content=None, title=None):
    try:
        if session.get("user_id"):
            db = sqlite3.connect("blog.db")
            c = db.cursor()

            user_id = session.get('user_id')
            blog_id = uuid4()
            post_date = str(datetime.datetime.now())[:19]

            # if the blog is being created from within another function, name will be
            # passed as an arg rather than as part of the request
            if name:
                blog_name = a_clean(name.title())
            else:
                blog_name = a_clean(request.form['blog_name']).title()

            # Ensures that no two blogs by the same user have the same blog_id / name
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

            c.execute(query)
            db.commit() 
            db.close()
            return create_post()
        return permissions()
    except:
        return render_template("error.html")

# ------------------------------------------------------------------------------
# Section for users' personal pages

@app.route("/user_page")
def user_page():
    try:
        if session.get("user_id"):
            user_id = session.get("user_id") ## TODO make home page work only if someone is logged in
            db = sqlite3.connect("blog.db")
            c = db.cursor()
            query = f"SELECT * FROM blogs WHERE user_id='{user_id}' ORDER BY post_date DESC"
            c.execute(query)
            blogs = list(c)
            db.close()
            return render_template("user_page.html", blogs=blogs) # user=username)
        return permissions()
    except:
        return render_template("error.html")

# allows users to have access to other people's blog pages from the main feed
@app.route("/other_blog_page", methods=["POST"])
def other_blog_page():
    try:
        if session.get("user_id"):
            other_user_id = request.form['other_user_id']
            blog_id = request.form['blog_id']

            db = sqlite3.connect("blog.db")
            c = db.cursor()

            query = f"SELECT blog_name FROM blogs where user_id='{other_user_id}' AND blog_id='{blog_id}'"
            c.execute(query)
            blog_name = tup_clean(list(c))[0]

            query = f"SELECT * FROM posts WHERE user_id='{other_user_id}' AND blog_id='{blog_id}' ORDER BY post_date DESC"
            c.execute(query)
            posts = list(c)

            return render_template("blog_page.html", posts=posts, blog_name=blog_name)
        return permissions()
    except:
        return render_template("error.html")


@app.route("/blog_page", methods=["POST"])
def blog_page():
    try:
        if session.get("user_id"):
            user_id = session.get('user_id')
            blog_id = request.form['blog_id']

            db = sqlite3.connect("blog.db")
            c = db.cursor()

            query = f"SELECT blog_name FROM blogs where user_id='{user_id}' AND blog_id='{blog_id}'"
            c.execute(query)
            blog_name = tup_clean(list(c))[0]

            query = f"SELECT * FROM posts WHERE user_id='{user_id}' AND blog_id='{blog_id}' ORDER BY post_date DESC"
            c.execute(query)
            posts = list(c)

            return render_template("blog_page.html", posts=posts, blog_name=blog_name)
        return permissions()
    except:
        return render_template("error.html")

@app.route("/other_user_page", methods=["POST"])
def other_user_pages():
    try:
        if session.get("user_id"):
            other_user_id = request.form["other_user_id"]

            # redirect you to your personal page if you try to
            # access it from within the feed (allows you to still edit)
            if other_user_id == session.get("user_id"):
                return user_page()

            db = sqlite3.connect("blog.db")
            c = db.cursor()
            query = f"SELECT * FROM blogs WHERE user_id='{other_user_id}'"
            c.execute(query)
            blogs = list(c)
            query = f"SELECT username FROM users WHERE user_id='{other_user_id}'"
            c.execute(query)
            username = tup_clean(list(c))[0]
            db.close()
            
            return render_template("other_user.html", blogs=blogs, username=username)
        else:
            return permissions()
    except:
        return render_template("error.html")
    
# ------------------------------------------------------------------------------
# Section for editing posts
@app.route("/edit_post", methods=["POST"])
def edit_post():
    try:
        if session.get("user_id"):
            db = sqlite3.connect("blog.db")
            c = db.cursor()
            user_id = session.get("user_id")
            post_id = request.form["post_id"]
            query = f"SELECT * FROM posts WHERE user_id='{user_id}' AND post_id='{post_id}'"
            c.execute(query)
            post = list(c)[0]
            db.close()
            return render_template("edit_post.html", post=post)
        else:
            return render_template("permissions.html")
    except:
        return render_template("error.html")
    

@app.route("/action_edit_post", methods=["POST"])
def action_edit_post():
    try:
        if session.get("user_id"):
            db = sqlite3.connect("blog.db")
            c = db.cursor()
            user_id = session.get("user_id")
            post_id = request.form["post_id"]
            content = a_clean(request.form["post_content"].strip())
            query = f"UPDATE posts SET content='{content}' WHERE post_id='{post_id}' AND user_id='{user_id}'"
            c.execute(query)
            db.commit()
            db.close()
            return user_page()
        else:
            return render_template("permissions.html")
    except:
        return render_template("error.html")
    
# ------------------------------------------------------------------------------


if __name__ == '__main__':
    app.debug = True
    app.run()
    
