import sys
sys.path.append("..")
from validators import validate_nick

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import DataRequired, EqualTo


class RegisterForm(FlaskForm):
    nickname = StringField('Логин пользователя', validators=[DataRequired(), validate_nick])
    password = PasswordField('Пароль', validators=[DataRequired(),
                                                   EqualTo('password_confirmation', message='Пароли должны совпадать')])
    password_confirmation = PasswordField('Подтвердите пароль', validators=[DataRequired()])

    is_teacher = BooleanField('Может создавать тесты и пользователей')

    submit = SubmitField('Сохранить')
