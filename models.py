from app import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash

# classes: User, Book, Recommendations?, Reading Lists? (for users to subscribe to)
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    category = db.Column(db.Integer, db.ForeignKey("category.id"))
    user = db.Column(db.Integer, db.ForeignKey("user.id"))
    date_added = db.Column(db.DateTime)
    read = db.Column(db.Boolean(), nullable=False)
    rating = db.Column(db.String(5), nullable=True)
    review = db.Column(db.String(5000), nullable=True)
    isbn = db.Column(db.String(20), nullable=True)
    

    # do I need to initialize book instances with rating, review, and isbn?
    def __init__(self, title, author, category, user, date_added, read=False, rating=None, review=None, isbn=None):
        self.title = title
        self.author = author
        self.category = category
        self.user = user
        self.date_added = date_added
        self.read = read
        self.rating = rating
        self.review = review
        self.isbn = isbn

    def __repr__(self):
        return f"<Book. Title: {self.title} Author: {self.author} Category: {self.category}>"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(60))
    email = db.Column(db.String(60), unique=True, nullable=False)
    pw_hash = db.Column(db.String(120), nullable=False)
    books = db.relationship("Book", backref="book.user")


    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.pw_hash = make_pw_hash(password)

    def __repr__(self):
        return f"<User. ID: {self.id} Email: {self.email}>"

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    books = db.relationship("Book", backref="book.category")

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"<Category: {self.name}>"


