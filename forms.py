from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
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