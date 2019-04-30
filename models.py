from app import db
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from hashutils import make_pw_hash

# classes: User, Book, Recommendations?, Reading Lists? (for users to subscribe to)
class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    author = db.Column(db.String(120), nullable=False)
    isbn = db.Column(db.Integer)
    reader = db.Column(db.Integer, db.ForeignKey("user.id"))

    def __init__(self, title, author, reader):
        self.title = title
        self.author = author
        self.reader = reader

    def __repr__(self):
        return f"<Book. Title: {self.title} Author: {self.author}>"

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(60))
    email = db.Column(db.String(60), unique=True, nullable=False)
    pw_hash = db.Column(db.String(120), nullable=False)
    books = db.relationship("Book", backref="book.reader")


    def __init__(self, first_name, last_name, email, password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.pw_hash = make_pw_hash(password)

    def __repr__(self):
        return f"<User. ID: {self.id} Email: {self.email}>"


