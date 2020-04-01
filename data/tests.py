import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase
from sqlalchemy_serializer import SerializerMixin


#association_table = sqlalchemy.Table('users_to_tests', SqlAlchemyBase.metadata,
 #   sqlalchemy.Column('user', sqlalchemy.Integer,
  #                    sqlalchemy.ForeignKey('users.id')),
   # sqlalchemy.Column('test', sqlalchemy.Integer,
    #                  sqlalchemy.ForeignKey('tests.id'))
#)


class Test(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'tests'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)

    questions = orm.relation("Question", back_populates='test')
    statistics = orm.relation("Result", back_populates='test')
    #users = orm.relation("User",
     #                    secondary="users_to_tests",
      #                   backref="test")

    def __repr__(self):
        return f"<Test> {self.id} {self.name}"
