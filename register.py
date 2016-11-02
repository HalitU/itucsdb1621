
from flask import Blueprint
from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField

register_app = Blueprint('register_app', __name__)

class RegisterForm(Form):
    name = StringField('Username')
    email = StringField('Email Address')
    password = PasswordField('Password')
    submit = SubmitField('Sign up')
