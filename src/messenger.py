from flask import Flask
from flask_ask import Ask, statement, question, session
import json
import requests
import time
import unidecode
import fbchat as fb

app = Flask(__name__)
ask = Ask(app, "/messenger")


def do_shit():
  pass


@app.route('/')
def homepage():
  return "Get Off My Lawn"


if __name__ == "__main__":
  app.run(debug=True)
