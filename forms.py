from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateField, SelectMultipleField, BooleanField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import Required

class LoginForm(FlaskForm):

    username = StringField('Username')
    password = StringField('Password')
    submit = SubmitField('Login')

class AddReq(FlaskForm):
    request = CheckboxInput