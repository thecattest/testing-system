import sys
sys.path.append("..")
from validators import validate_email

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired, EqualTo


class RegisterForm(FlaskForm):
    email = EmailField('Your Email', validators=[DataRequired(), validate_email])
    password = PasswordField('Password', validators=[DataRequired(),
                                                   EqualTo('password_confirmation', message='Passwords must match')])
    password_confirmation = PasswordField('Repeat Password', validators=[DataRequired()])

    surname = StringField("Your Surname", validators=[DataRequired()])
    name = StringField("Your Name", validators=[DataRequired()])
    age = IntegerField("Your age", validators=[DataRequired()])

    position = StringField("Your Position", validators=[DataRequired()])
    speciality = StringField("Speciality", validators=[DataRequired()])

    address = StringField("Your address", validators=[DataRequired()])

    submit = SubmitField('Register')