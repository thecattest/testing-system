import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


association_table = sqlalchemy.Table('groups_to_users', SqlAlchemyBase.metadata,
    sqlalchemy.Column('user', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('users.id')),
    sqlalchemy.Column('group', sqlalchemy.Integer,
                     sqlalchemy.ForeignKey('groups.id'))
)


class Group(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'groups'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    is_service = sqlalchemy.Column(sqlalchemy.Boolean, default=0)
    for_all_users = sqlalchemy.Column(sqlalchemy.Boolean, default=0)

    creator = orm.relation("User")
    users = orm.relation("User",
                         secondary="groups_to_users",
                         backref="group")

    def __repr__(self):
        return f"<Group {self.id} {self.name} {self.creator.nick}>"