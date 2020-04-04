import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


class ResultRow(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'result_row'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    q_id = sqlalchemy.Column(sqlalchemy.Integer)
    result_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("result.id"))
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    answer = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=None)
    correct = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    result = orm.relation("Result")

    def __repr__(self):
        return f"<ResultRow {self.q_id} {self.answer} {self.result}>"
