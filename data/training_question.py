import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


class TrainingQuestion(SqlAlchemyBase):
    __tablename__ = 'training_question'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    q_id = sqlalchemy.Column(sqlalchemy.Integer)
    training_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("training.id"))
    text = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    answer = sqlalchemy.Column(sqlalchemy.String, nullable=True, default=None)
    correct = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    mistakes = sqlalchemy.Column(sqlalchemy.Integer, nullable=False, default=0)

    training = orm.relation("Training")

    def __repr__(self):
        return f"<TrainingQuestion {self.q_id} {self.answer} {self.correct}>"
