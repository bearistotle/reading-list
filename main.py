from flask import Flask, render_template, redirect, request, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, Email, EqualTo
from werkzeug import security
from app import db, app
from models import User, Book
from forms import LoginForm, RegistrationForm


#routes: index, reading now, coming up, full list, settings (sub settings 
# options for weights, categories, priorities, ratios?), subscribable 
# reading lists, . . .


@app.route('/', methods=['GET', 'POST'])
@app.route('/home', methods=['GET', 'POST'])
def home():
    email = session['user']
    user = User.query.filter_by(email=email).first()
    current_list = Book.query.filter_by(reader=user.id)
    return render_template('home.html')

@app.before_request
def require_login():
    if not ('user' in session or request.endpoint in ['login', 'register']):
        return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'GET':
        return render_template('login.html', title='Log In', form=form)

    else:
        email = form.email.data
        password = form.password.data

        if not User.query.filter_by(email=email):
            flash('Invalid username or password.')
            return render_template('login.html', title='Log In', form=form)

        user = User.query.filter_by(email=email).first()


        if not security.check_password_hash(user.hashed_pass, password):
            flash('Invalid username or password.')
            return render_template('login.html', title='Log In', form=form)

        session['user'] = email
        return redirect('/')

@app.route('/register', methods=['GET', 'POST'])
def register():

    form = RegistrationForm()

    if request.method == 'GET':
        return render_template('register.html', title='Register', form=form)

    if request.method == 'POST':

        if form.validate_on_submit():
            email = form.email.data

            # final step in validation: unique email/not existing user
            if User.query.filter_by(email=email).first():
                flash('A user with that email address already exists!')
                return render_template('register.html', title='Register', form=form)
            
            else:
                
                # generate hash to store in db instead of password
                hashed_pass = security.generate_password_hash(form.password.data, method='pbkdf2:sha256', salt_length=16)


                user = User(form.first_name.data, form.last_name.data, email, hashed_pass)
                db.session.add(user)
                db.session.commit()

                flash(f'Account created for {email}!')
                session['user'] = email
                return redirect(url_for('home'))
        
        else:
            return render_template('register.html', title='Register', form=form)

      

if __name__ == '__main__':
    app.run()
