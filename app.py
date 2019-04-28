from flask import Flask
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)


app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://reading-list:4books@localhost:8889/reading-list'
app.config['SQLALCHEMY_ECHO'] = True

app.config['SECRET_KEY'] = 'e5091fc606601b21fa7a7a730ec92aa0'

db = SQLAlchemy(app)