import sqlalchemy
from sqlalchemy import orm
import datetime

from .db_session import SqlAlchemyBase


class Training(SqlAlchemyBase):
    __tablename__ = 'training'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    test_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('tests.id'))
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('users.id'))
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, default=0)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())

    test = orm.relation("Test")
    user = orm.relation('User')
    questions = orm.relation("TrainingQuestion", back_populates="training")

    def __repr__(self):
        return f"<Training {self.id} {self.name} {self.is_finished}>"
