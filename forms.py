from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, DateField, SelectField
from wtforms.widgets import ListWidget, CheckboxInput
from wtforms.validators import Required
from state_district import state

class LoginForm(FlaskForm):

    username = StringField('Username')
    password = StringField('Password')
    submit = SubmitField('Login')

class AddStalkCollector(FlaskForm):

    name = StringField('Enter the name')
    contact_no = StringField('Enter the contact number')
    state = SelectField('Select State', choices=list(zip(state.values(), state.keys())))
    district_name = SelectField('Select District', choices=[])
    submit = SubmitField('Submit')