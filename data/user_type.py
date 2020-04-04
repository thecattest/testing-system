import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class UserType(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'user_types'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)

    users = orm.relation("User", back_populates="user_type")

    def __repr__(self):
        return f"<UserType {self.id} {self.name}>"
