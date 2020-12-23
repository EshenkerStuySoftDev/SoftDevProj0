# Third Huge Freckled Elephant
# Ethan Shenker, Constance Chen, Andrew Jiang, Saqif Abedin
# P0 - To Be Named
# 2020-12-xx

from flask import Flask, render_template, session, request
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)

@app.route("/")
def landing():
    return render_template("launch.html")

@app.route("/test")
def test():
    return render_template("test.html")


if __name__ == '__main__':
    app.debug = True
    app.run()
    