from flask import Flask, render_template, redirect, request
from flask import session, flash, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired, Length, Email, EqualTo
from app import db, app, service
from models import User, Book, Category
from forms import LoginForm, RegistrationForm, AddBookForm, RateReviewForm
from forms import SearchForm
from hashutils import check_pw_hash
from datetime import datetime
from googleapiclient.discovery import build
import json

# routes: index, reading now, coming up, full list, settings (sub settings
# options for weights, categories, priorities, ratios?), subscribable
# reading lists, . . .

# TODO: change text of book title and author to proper capitalization on
# display? (store lower?)


@app.before_request
def require_login():

    if not ("user" in session or request.endpoint in ["login", "register"]):
        return redirect(url_for("login"))

@app.route("/", methods=["GET"])
@app.route("/home", methods=["GET"])
def home():
    # form for search in navbar (since this is the same for all routes,
    # except login and register, this should probably be set in the app.py
    # file with other configuration stuff)
    search_form = SearchForm()

    # determine the user
    email = session["user"]
    user = User.query.filter_by(email=email).first()

    #get list of unread books by user and sort it by date_added
    book_list = Book.query.filter_by(user=user.id, read=False).all()
    book_list = sorted(book_list, key=lambda x: x.date_added)


    # if 3 or fewer books, display all books
    if len(book_list) <= 3:

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

        # note: need to wrap zip in list in Py 3x bc zip rtns iterable not list
        # (what is the difference? iterables don't support indexing?)
        current_list = list(zip(book_list, category_list, style_list))

        return render_template("home.html", current=current_list, search_form=search_form)

    # if more than 3 books, display first book from ea category
    else:

        current_books = []
        i = 1
        
        # the initial problem with this loop was that it didn't start over from
        #  the beginning when a book was appended. It could pass over the first 
        # book in the cat before finding the first book in the previous cat
        # and it won't come back to it. Now it just adds the first book a bunch.
        # Finally fixed it! Not the best way probably

        # TODO: Refactor while loop to be more elegant/efficient. Perhaps use 
        # next()? Or define a helper function?
        while len(current_books) < 3:
            for book in book_list:
                if book.category == i:

                    earlier_bk_in_cat = False

                    for tome in current_books:

                        if tome.category == i:
                            earlier_bk_in_cat = True
                            break

                    if earlier_bk_in_cat == False:
                        current_books.append(book)
                        break

            i += 1

        category_list = []
        [category_list.append(Category.query.filter_by(id=book.category).first()) for book in current_books]

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

        current_list = list(zip(current_books, category_list, style_list))

        # if booklist < 6, add all over 3 to upcoming
        upcoming_books = []
        if len(book_list) <= 6:
            for book in book_list:
                if book not in current_books:
                    upcoming_books.append(book)
            
            category_list = []
            [category_list.append(Category.query.filter_by(id=book.category).first()) for book in upcoming_books]

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
            
            upcoming_list = list(zip(upcoming_books, category_list, style_list))

        # else add 4, 5, 6 to upcoming
        else:

            i = 1
            while len(upcoming_books) < 3:
                for book in book_list:
                    if book not in current_books:

                        if book.category == i:

                            earlier_bk_in_cat = False

                            for tome in upcoming_books:

                                if tome.category == i:
                                    earlier_bk_in_cat = True
                                    break

                            if earlier_bk_in_cat == False:
                                upcoming_books.append(book)
                                break

                i += 1

            category_list = []
            [category_list.append(Category.query.filter_by(id=book.category).first()) for book in upcoming_books]

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
            
            upcoming_list = list(zip(upcoming_books, category_list, style_list))

        return render_template("home.html", current=current_list,
                               upcoming=upcoming_list,
                               search_form=search_form)


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

    # form for search in navbar (since this is the same for all routes,
    # except login and register, this should probably be set in the app.py
    # file with other configuration stuff)
    search_form = SearchForm()

    # get user
    email = session["user"]
    user = User.query.filter_by(email=email).first()
    book_list = Book.query.filter_by(user=user.id, read=False).all()
    category_list = []
    
    [category_list.append(Category.query.filter_by(id=book.category).first())
    for book in book_list]

    book_category_list = list(zip(book_list, category_list))

    form = AddBookForm()

    if request.method == "GET":

        if request.args:
            book = Book.query.filter_by(id=request.args.get("book_id")).first()
            book.category = int(request.args.get("category_id"))

            db.session.commit()

            return redirect(url_for("edit_list"))

        return render_template("edit-list.html", form=form, search_form=search_form, list=book_category_list)

    if form.validate_on_submit():

        # get form data
        title = form.title.data
        author = form.author.data
        category = form.category.data
        user = user.id
        date_added = datetime.utcnow()
        read = False
        rating = None
        review = None
        isbn = form.isbn.data

        book = Book(title, author, category, user, date_added, read, rating, review, isbn)

        db.session.add(book)
        db.session.commit()

        flash(f"{title} added to reading list!")

        return redirect(url_for("edit_list"))

    for error in form.errors.items():

        flash(f"{error[1][0]}!", "error")

    return render_template("edit-list.html", form=form, search_form=search_form,
                           list=book_category_list)


@app.route("/remove-book", methods=["GET"])
def remove_book():
    # form for search in navbar (since this is the same for all routes,
    # except login and register, this should probably be set in the app.py
    # file with other configuration stuff)
    search_form = SearchForm()

    if request.args:

        book_id = request.args.get("id")
        book = Book.query.get(book_id)

        db.session.delete(book)
        db.session.commit()

        flash(f"{book.title} removed from reading list!", "info")

    return redirect(url_for("edit_list"))


@app.route("/reading-history", methods=["GET", "POST"])
def reading_history():
    # form for search in navbar (since this is the same for all routes,
    # except login and register, this should probably be set in the app.py
    # file with other configuration stuff)
    search_form = SearchForm()

    form = RateReviewForm()

    if request.args.get("id"):

        book_id = request.args.get("id")
        book = Book.query.get(book_id)

        # send user to rating and review form
        return render_template("rate-review.html", form=form, search_form=search_form, book=book)

    if request.method == "POST":

        rating = form.rating.data
        review = form.review.data
        book_id = form.book_id.data

        book = Book.query.get(book_id)

        book.rating = rating
        book.review = review
        book.read = True
        book.date_read = datetime.utcnow()

        db.session.commit()
        flash(f"{book.title} added to your reading history.", "info")

    # user should fall through to this point if GET with no args or POST after
    # form data has been validated and db has been updated
    user_email = session["user"]
    user = User.query.filter_by(email=user_email).first()
    read_books = Book.query.filter_by(user=user.id, read=True).all()

    review_snippets = []
    for book in read_books:
        snippet = book.review[:200]
        review_snippets.append(snippet)
    
    history = list(zip(read_books, review_snippets))

    return render_template("reading-history.html", search_form=search_form, history=history)


@app.route("/snooze", methods=["GET"])
def snooze():
    
    if request.args:
        book = Book.query.filter_by(id=request.args.get("id")).first()

        # send book to end of list (reset date_added)

        book.date_added = datetime.utcnow()


        db.session.commit()


    return redirect(url_for("home"))

@app.route("/full-review", methods=["GET"])
def full_review():

    if request.args:

        book = Book.query.get(request.args.get("id"))

        return render_template("full-review.html", book=book, search_form=search_form)
        
    return redirect(url_for("reading_history"))


@app.route("/search-results", methods=["POST"])
def search_results():

    search_form = SearchForm()
    add_book_form = AddBookForm()
    search_type = search_form.search_type.data
    search_term = search_form.search_term.data
    query = search_type + "+" + search_term


    # access credentials file to get API_KEY
    with open("credentials.json") as creds:
        secrets = json.load(creds)

    # create service object to build requests
    service = build('books', 'v1', developerKey=secrets["credentials"]["API_KEY"])

    # Create request object. Returns an apiclient.http.HttpRequest object that
    # encapsulates all information needed to make the request, but it does not
    # call the API.
    request = service.volumes().list(source="public", q=query)

    # Execute request. It returns a Python object built from the JSON response.
    # You can print this object or refer to the Books API documentation to
    # determine its structure.
    response = request.execute()

    # Create results object to pass into render_template
    results = []

    for book in response.get('items', []):

        title = book["volumeInfo"]["title"]
        authors = book["volumeInfo"]["authors"]
        num_authors = len(book["volumeInfo"]["authors"])

        if book["volumeInfo"].get("industryIdentifiers"):

            if book["volumeInfo"]["industryIdentifiers"][0].get("identifier"):

                isbn_13 = book["volumeInfo"]["industryIdentifiers"][0]["identifier"]

        else:
            isbn_13 = "No ISBN-13 available."

        results.append({"title": title, "authors": authors, "num_authors": num_authors, "isbn_13": isbn_13})


    return render_template("search-results.html", search_form=search_form,
                           add_book_form=add_book_form, results=results)
    

if __name__ == "__main__":
    app.run()
