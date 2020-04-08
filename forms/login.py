from flask_wtf import FlaskForm
from wtforms import PasswordField, SubmitField, StringField, BooleanField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    nickname = StringField('Ваш логин', validators=[DataRequired()])
    password = PasswordField('Ваш пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')