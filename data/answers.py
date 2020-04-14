import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class Answer(SqlAlchemyBase):
    __tablename__ = 'answers'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    is_correct = sqlalchemy.Column(sqlalchemy.Boolean, nullable=False, default=False)
    question_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("questions.id"))

    question = orm.relation("Question")

    def __repr__(self):
        return f"<Answer {self.id} {self.text} {self.question_id}>"
