from flask import Flask, render_template, redirect, request, session, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug import security
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

    def __init__(self, title, author):
        self.title = title
        self.author = author

    def __repr__(self):
        return '<Book. Title: {0} Author: {1}>'.format(self.title, self.author)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(60))
    email = db.Column(db.String(60), unique=True, nullable=False)
    salt = db.Column(db.Integer, unique=True, nullable=False)
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
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, book_id, user_id):
        self.book_id = book_id
        self.user_id = user_id

    def __repr__(self):
        return '<ReadingList. Book: {0} User: {1}'.format(self.book_id, self.user_id)



#routes: index, reading now, coming up, full list, settings (sub settings 
# options for weights, categories, priorities, ratios?), subscribable 
# reading lists, . . .


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    user = session['user']
    current_list = ReadingList.query.filter_by(user_id=user.id)
    return render_template('home.html')
'''
@app.before_request
def require_login():
    if not session['user'] and routes.endpoint not in ['login', 'register']:
        return redirect('/login')
'''
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    else:
        email = request.form['email']
        password = request.form['password']

        if not User.query.filter_by(email=email):
            flash('Invalid username or password.')
            return render_template('login.html')

        user = User.query.filter_by(email=email)


        if not security.check_password_hash(user.hash, password):
            flash('Invalid username or password.')
            return render_template('login.html')

        session['user'] = user.email
        return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():
    # pull data from form
    # gen salt with urandom (at least as long as hash)
    # hash password + salt
    # store salt and hashed_pass in db


if __name__ == '__main__':
    app.run()
