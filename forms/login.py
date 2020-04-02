from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField, BooleanField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    nickname = StringField('Your nickname', validators=[DataRequired()])
    password = PasswordField('Your password', validators=[DataRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('Log in')