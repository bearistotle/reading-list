from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from googleapiclient.discovery import build
import json

app = Flask(__name__)

with open('credentials.json') as creds:
    secrets = json.load(creds)

db_name = secrets["credentials"]["db_name"]
db_pw = secrets["credentials"]["db_pw"]

app.config["DEBUG"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = f"mysql+pymysql://{db_name}:{db_pw}@localhost:8889/reading-list"
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = secrets["credentials"]["APP_SECRET_KEY"]


service = build("books", "v1", developerKey=secrets["credentials"]["API_KEY"])

db = SQLAlchemy(app)