from flask import Flask, render_template, redirect, request
from flask import session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, Email, EqualTo
from app import db, app
from models import User, Book, Category
from forms import LoginForm, RegistrationForm, AddBookForm, RateReviewForm
from hashutils import check_pw_hash

# routes: index, reading now, coming up, full list, settings (sub settings
# options for weights, categories, priorities, ratios?), subscribable
# reading lists, . . .

# TODO: change text to title capitalization on display (store lower?)


@app.before_request
def require_login():

    if not ("user" in session or request.endpoint in ["login", "register"]):
        return redirect(url_for("login"))


@app.route("/", methods=["GET"])
@app.route("/home", methods=["GET"])
def home():

    email = session["user"]
    user = User.query.filter_by(email=email).first()
    book_list = Book.query.filter_by(user=user.id, read=False).all()

    if len(book_list) < 3:

        

        category_list = []
        [category_list.append(Category.query.filter_by(id=book.category).first()) for book in book_list]
    
        style_list = []
            
        # would this be better as a list comp? Prob not bc of multiple conditions?
        for category in category_list:
            if category.name == "5 Mins to Kill":
                style = "table-success"
            elif category.name == "Relax/Escape":
                style = "table-info"
            elif category.name == "Focused Learning":
                style = "table-warning"
            else:
                style = "table-secondary"
            
            style_list.append(style)

        # need to wrap zip in list in Py 3x bc zip rtns iterable not list
        book_cat_style_list = list(zip(book_list, category_list, style_list))

        return render_template("home.html", list=book_cat_style_list)

    else:

        # append current list with first bk from ea. category
        user_id = User.query.filter_by(email=session["user"]).first().id

        book_list = []
        [book_list.append(Book.query.filter_by(category=i, user=user_id).first()) for i in range(1, 4)]

        category_list = []
        [category_list.append(Category.query.filter_by(id=book.category).first()) for book in book_list]

        style_list = []
        for category in category_list:
            if category.name == "5 Mins to Kill":
                style = "table-success"
            elif category.name == "Relax/Escape":
                style = "table-info"
            elif category.name == "Focused Learning":
                style = "table-warning"
            else:
                style = "table-secondary"
            
            style_list.append(style)

        current_list = list(zip(book_list, category_list, style_list))

        return render_template("home.html", list=current_list)


@app.route("/login", methods=["GET", "POST"])
def login():

    form = LoginForm()
    if request.method == "GET":
        return render_template("login.html", title="Log In", form=form)

    else:

        email = form.email.data.lower()
        password = form.password.data

        if not User.query.filter_by(email=email).first():

            flash("Invalid username or password.", "error")
            return render_template("login.html", title="Log In", form=form)

        user = User.query.filter_by(email=email).first()

        if not check_pw_hash(password, user.pw_hash):

            flash("Invalid username or password.", "error")
            return render_template("login.html", title="Log In", form=form)

        session["user"] = email
        return redirect(url_for("home"))


@app.route("/register", methods=["GET", "POST"])
def register():

    form = RegistrationForm()

    if request.method == "GET":
        return render_template("register.html", title="Register", form=form)

    if form.validate_on_submit():

        first_name = form.first_name.data
        last_name = form.last_name.data
        email = form.email.data.lower()
        password = form.password.data

        # final step in validation: unique email/not existing user
        if User.query.filter_by(email=email).first():

            flash("A user with that email address already exists!", "error")

            return render_template("register.html", title="Register",
                                   form=form)

        else:
            # password hashed by constructor of User model
            user = User(first_name, last_name, email, password)
            db.session.add(user)
            db.session.commit()

            flash(f"Account created for {email}!")
            session["user"] = email

            return redirect(url_for("home"))

    else:

        for error in form.errors.items():

            flash(f"{error[1][0]}!", "error")

        return render_template("register.html", title="Register", form=form)


@app.route("/logout", methods=["GET"])
def logout():

    del session["user"]

    return redirect(url_for("login"))


@app.route("/edit-list", methods=["GET", "POST"])
def edit_list():

# TODO: Refactor to move processing from templates to main

# TODO: allow change of category via dropdown selection in table row

    # get user
    email = session["user"]
    user = User.query.filter_by(email=email).first()
    book_list = Book.query.filter_by(user=user.id, read=False).all()
    category_list = []
    
    [category_list.append(Category.query.filter_by(id=book.category).first()) for book in book_list]

    book_category_list = list(zip(book_list, category_list))

    form = AddBookForm()

    if request.method == "GET":
        return render_template("edit-list.html", form=form,
                               list=book_category_list)

    if form.validate_on_submit():

        # get form data
        title = form.title.data
        author = form.author.data
        category = form.category.data
        user = user.id
        read = False
        rating = None
        review = None
        isbn = form.isbn.data

        book = Book(title, author, category, user, read, rating, review, isbn)

        db.session.add(book)
        db.session.commit()

        flash(f"{title} added to reading list!")

        return redirect(url_for("edit_list"))

    for error in form.errors.items():

        flash(f"{error[1][0]}!", "error")

    return render_template("edit-list.html", form=form,
                           list=book_with_category)


@app.route("/remove-book", methods=["GET"])
def remove_book():

    if request.args:

        book_id = request.args.get("id")
        book = Book.query.get(book_id)

        db.session.delete(book)
        db.session.commit()

        flash(f"{book.title} removed from reading list!", "info")

    return redirect(url_for("edit_list"))


@app.route("/reading-history", methods=["GET", "POST"])
def reading_history():

    form = RateReviewForm()

    if request.args.get("id"):

        book_id = request.args.get("id")
        book = Book.query.get(book_id)

        # send user to rating and review form
        return render_template("rate-review.html", form=form, book=book)

    if request.method == "POST":

        rating = form.rating.data
        review = form.review.data
        book_id = form.book_id.data

        book = Book.query.get(book_id)

        book.rating = rating
        book.review = review
        book.read = True

        db.session.commit()
        flash(f"{book.title} added to your reading history.", "info")

    # user should fall through to this point if GET with no args or POST after
    # form data has been validated and db has been updated
    user_email = session["user"]
    user = User.query.filter_by(email=user_email).first()
    history = Book.query.filter_by(user=user.id, read=True)

    return render_template("reading-history.html", history=history)


if __name__ == "__main__":
    app.run()
