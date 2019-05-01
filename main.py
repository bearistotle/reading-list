from flask import Flask, render_template, redirect, request, session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, Email, EqualTo
from app import db, app
from models import User, Book
from forms import LoginForm, RegistrationForm, AddBookForm
from hashutils import check_pw_hash

#routes: index, reading now, coming up, full list, settings (sub settings 
# options for weights, categories, priorities, ratios?), subscribable 
# reading lists, . . .

# TODO: create route/handler and template for reading-history

@app.before_request
def require_login():

    if not ("user" in session or request.endpoint in ["login", "register"]):
        return redirect(url_for("login"))

@app.route("/", methods=["GET"])
@app.route("/home", methods=["GET"])
def home():

    email = session["user"]
    user = User.query.filter_by(email=email).first()
    current_list = Book.query.filter_by(reader=user.id).all()

    return render_template("home.html", current_list=current_list)

@app.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()
    if request.method == "GET":
        return render_template("login.html", title="Log In", form=form)

    else:

        email = form.email.data
        password = form.password.data

        if not User.query.filter_by(email=email):
            flash("Invalid username or password.")
            return render_template("login.html", title="Log In", form=form)

        user = User.query.filter_by(email=email).first()


        if not check_pw_hash(password, user.pw_hash):

            flash("Invalid username or password.")
            return render_template("login.html", title="Log In", form=form)

        session["user"] = email
        return redirect("/")

@app.route("/register", methods=["GET", "POST"])
def register():

    form = RegistrationForm()

    if request.method == "GET":
        return render_template("register.html", title="Register", form=form)

    if form.validate_on_submit():

        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data
        password = form.password.data

        # final step in validation: unique email/not existing user
        if User.query.filter_by(email=email).first():
            flash("Error! A user with that email address already exists!")
            return render_template("register.html", title="Register", form=form)
        
        else:
            # password hashed by constructor of User model
            user = User(first_name, last_name, email, password)
            db.session.add(user)
            db.session.commit()

            flash(f"Success! Account created for {email}!")
            session["user"] = email
            return redirect(url_for("home"))
        
    else:

        for error in form.errors.items():
                flash(f"Error! {error[1][0]}")

        return render_template("register.html", title="Register", form=form)

@app.route("/logout", methods=["GET"])
def logout():
    del session["user"]
    return redirect(url_for("login"))

@app.route("/edit-list", methods=["GET", "POST"])
def edit_list():

    # get user
    email = session["user"]
    user = User.query.filter_by(email=email).first()
    current_list = Book.query.filter_by(reader=user.id).all()
    form = AddBookForm()

    if request.method == "GET":
        return render_template("edit-list.html", form=form,
            current_list=current_list)

    if form.validate_on_submit():

        # get form data
        title = form.title.data
        author = form.author.data
        isbn = form.isbn.data
        reader = user.id

        book = Book(title, author, reader, isbn)

        db.session.add(book)
        db.session.commit()

        flash(f"{title} added to reading list!")
        return redirect(url_for("edit_list"))
    
    for error in form.errors.items():
        flash(f"Error! {error[1][0]}")

    return render_template("edit-list.html", form=form)

@app.route("/remove-book", methods=["GET"])
def remove_book():
    if request.args:
        book_id = request.args.get("id")
        book = Book.query.get(book_id)

        db.session.delete(book)
        db.session.commit()

    return redirect(url_for("edit_list"))

@app.route("/reading-history", methods=["GET", "POST"])
def reading_history():
    if request.args:
        book_id = request.args.get("id")
        book = Book.query.get(book_id)

        form = RateReviewForm()

        # send user to rating and review form
        # once user fills out form, have it post here
        # process form data
        # user should fall through to simply rendering reading history template
        # (it should be a GET with no args)

        # TODO: drop and create tables to update Book model; finish rate-review template
    

if __name__ == "__main__":
    app.run()
