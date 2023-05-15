from flask import Flask
from threading import Thread

app = Flask("")


@app.route("/")
def home():
    return "I'm alive"


def run():
    app.run()


def keep_alive():
    t = Thread(target=run)
    t.start()
