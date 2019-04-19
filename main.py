from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://reading-list:4books@localhost:8889/reading-list'
app.config['SQLALCHEMY_ECHO'] = True

app.secret_key = '2d6Wz5oVayqYKZr'

db = SQLAlchemy(app)


# classes: User, Book, Recommendations?, Reading Lists? (for users to subscribe to)

#routes: index, reading now, coming up, full list, settings (sub settings 
# options for weights, categories, priorities, ratios?), subscribable 
# reading lists, . . .


if __name__ == '__main__':
    app.run()
    