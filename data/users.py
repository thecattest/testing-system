import sqlalchemy
from sqlalchemy import orm

from werkzeug.security import check_password_hash, generate_password_hash

from .db_session import SqlAlchemyBase
from flask_login import UserMixin
from sqlalchemy_serializer import SerializerMixin


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    type_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("user_types.id"), default=3)

    results = orm.relation("Result", back_populates='user')
    user_type = orm.relation("UserType")
    created = orm.relation("User")
    created_groups = orm.relation("Group", back_populates='creator')
    groups = orm.relation("Group",
                          secondary="groups_to_users",
                          backref="user")

    #tests = orm.relation("Test",
     #                    secondary="users_to_tests",
      #                   backref="user")

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"<User {self.id} {self.nickname}>"
