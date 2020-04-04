from data import db_session
from data.__all_models import *
from wtforms.validators import ValidationError


def validate_nick(form, field):
    session = db_session.create_session()
    user = session.query(User).filter(User.nickname == field.data).first()
    if not user is None:
        raise ValidationError('Пользователь с таким ником уже существует')