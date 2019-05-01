from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, TextAreaField, HiddenField
from wtforms.validators import InputRequired, Length, Email, EqualTo, Optional

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(),
        Email(message="Not a valid email address.")])
    password = PasswordField("Password", validators=[InputRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField("Log In")

class RegistrationForm(FlaskForm):
    first_name = StringField("First Name", validators=[InputRequired(), 
        Length(min=3, max=20)])
    last_name = StringField("Last Name", validators=[InputRequired(), 
        Length(min=3, max=40)])
    email = StringField("Email", validators=[InputRequired(),
        Email(message="Not a valid email address.")])
    password = PasswordField("Password", validators=[InputRequired(), 
        Length(min=8, max=25, message="""Password must be between 8 and 25 
            characters.""")])
    confirm = PasswordField("Verify Password", validators=[InputRequired(), 
        EqualTo("password", message="Passwords don't match.")])
    submit = SubmitField("Register")

class AddBookForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired(), 
        Length(min=3, max=150)])
    author = StringField("Author (Last, First)", validators=[InputRequired(), 
        Length(min=3, max=120)])
    isbn = StringField("ISBN (Optional)", validators=[Optional(), Length(min=10, max=13)])
    submit = SubmitField("Add Book")

class RateReviewForm(FlaskForm):
    rating = SelectField("Rating", choices=[(1, "*"), (2, "**"), (3, "***"), (4, "****"), (5, "*****")])
    review = TextAreaField("Review", validators=[Optional(), Length(min=0, max=5000)])
    book_id = HiddenField() # better validators? # what to do on err?
    submit = SubmitField("Mark as Read")