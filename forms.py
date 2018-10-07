from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField

class LoginForm(FlaskForm):

    username = StringField('Username')
    password = StringField('Password')
    submit = SubmitField('Login')

