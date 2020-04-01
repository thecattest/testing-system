import sqlalchemy
from sqlalchemy import orm
import datetime

from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class Result(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'result'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    test_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey('tests.id'))
    is_finished = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    end_date = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())

    test = orm.relation("Test")
    rows = orm.relation("ResultRow", back_populates="result")

    def __repr__(self):
        return f"<Result> {self.id} {self.name} {self.is_finished}"
