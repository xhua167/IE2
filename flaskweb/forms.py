from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError

from flaskweb import db


class RegistrationForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=6, max=20)])
    confirm_password = PasswordField('Confirm Password',
                                     validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign up')

    def validate_username(self,username):
        user = db.user.find_one({'username': username.data})
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self,email):
        user = db.user.find_one({"email": email.data})
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')


class LoginForm(FlaskForm):
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=6)])
    remenber = BooleanField('Remember me')
    submit = SubmitField('Login')

class RatingForm(FlaskForm):
    rating = StringField('Rating')
    submit = SubmitField('Submit')

class SearchForm(FlaskForm):
    search = StringField('Search',
                           validators=[DataRequired(), Length(max=20)])
    submit = SubmitField('Search')

class FavoriteForm(FlaskForm):
    favorite = StringField('Favorite')
    submit = SubmitField('Favorite')