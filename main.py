from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)


app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://reading-list:4books@localhost:8889/reading-list'
app.config['SQLALCHEMY_ECHO'] = True

app.secret_key = '2d6Wz5oVayqYKZr'

db = SQLAlchemy(app)


# classes: User, Book, Recommendations?, Reading Lists? (for users to subscribe to)

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    isbn = db.Column(db.Integer, unique=True)

    def __init__(self, title, author)
    self.title = title
    self.author = author

    def __repr__(self):
        return '<Book. Title: {0} Author: {1}>'.format(self.title, self.author)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(60))
    email = db.Column(db.String(60), unique=True nullable=False)
    hashed_pass = db.Column(db.String(60), nullable=False)

    def __init__(self, first_name, last_name, email, hashed_pass):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.hashed_pass = hashed_pass

    def __repr__(self):
        return '<User. ID: {0} Email: {1}'.format(self.id, self.email)

class ReadingList(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, ForeignKey('book.id'))
    user_id = db.Column(db.Integer, ForeignKey('user.id'))

    def __init__(self, book_id, user_id):
        self.book_id = book_id
        self.user_id = user_id

    def __repr__(self):
        return '<ReadingList. Book: {0} User: {1}'.format(self.book_id, self.user_id)



#routes: index, reading now, coming up, full list, settings (sub settings 
# options for weights, categories, priorities, ratios?), subscribable 
# reading lists, . . .


if __name__ == '__main__':
    app.run()
