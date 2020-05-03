import sqlalchemy
from sqlalchemy import orm
from random import sample
from hashlib import md5

from werkzeug.security import check_password_hash, generate_password_hash

from .db_session import SqlAlchemyBase
from flask_login import UserMixin


class User(SqlAlchemyBase, UserMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    nickname = sqlalchemy.Column(sqlalchemy.String, unique=True, nullable=False)
    hashed_password = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    type_id = sqlalchemy.Column(sqlalchemy.Integer,
                                sqlalchemy.ForeignKey("user_types.id"), default=3)
    secret_code = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    chat_id = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    results = orm.relation("Result", back_populates='user')
    user_type = orm.relation("UserType")
    notifications = orm.relation("Notification", back_populates='user')
    created = orm.relation("User")
    tests = orm.relation("Test", back_populates='creator')
    created_groups = orm.relation("Group", back_populates='creator')
    groups = orm.relation("Group",
                          secondary="groups_to_users")

    def set_secret_code(self):
        hash = md5(self.nickname.encode())
        hex_hash = hash.hexdigest()
        symbols = sample(list(hex_hash), 5)
        self.secret_code = "".join(symbols)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def __repr__(self):
        return f"<User {self.id} {self.nickname}>"
