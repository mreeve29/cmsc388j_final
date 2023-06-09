from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, SelectField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import (
    InputRequired,
    DataRequired,
    NumberRange,
    Length,
    Email,
    EqualTo,
    ValidationError,
)

import re

from .models import User

class AddToFavoritesForm(FlaskForm):
    submit = SubmitField(label="Add to Favorites", render_kw={'class':'btn btn-success rating-btn mx-auto'})

class RemoveFromFavoritesForm(FlaskForm):
    submit = SubmitField(label="Remove from Favorites", render_kw={'class':'btn btn-danger rating-btn mx-auto'})


class SearchForm(FlaskForm):
    search_query = StringField(
        "Query", validators=[InputRequired(), Length(min=1, max=100)]
    )
    submit = SubmitField("Search")


class RestaurantReviewForm(FlaskForm):
    text = TextAreaField(
        "Comment", validators=[InputRequired(), Length(min=5, max=500)]
    )
    stars = SelectField(
        "Stars", choices=[5,4,3,2,1], coerce=int, validators=[InputRequired(), NumberRange(min=1, max=5)]
    )
    submit_review = SubmitField("Submit Review")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken")

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError("Email is taken")
        
    def validate_password(self, password):
        p = password.data
        if len(p) < 12:
            raise ValidationError("Password must be at least 12 characters")
        if not bool(re.search(r'[A-Z]', p)):
            raise ValidationError("Password must have an uppercase character")
        if not bool(re.search(r'[a-z]', p)):
            raise ValidationError("Password must have a lowercase character")
        if not bool(re.search(r'[#@$&!]', p)):
            raise ValidationError("Password must contain a special character")
        if p[0] == ' ' or p[-1] == ' ':
            raise ValidationError("Password cannot start or end with a space")


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")


class UpdateUsernameForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    submit = SubmitField("Change Username")

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.objects(username=username.data).first()
            if user is not None:
                raise ValidationError("That username is already taken")
