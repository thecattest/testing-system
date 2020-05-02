import sqlalchemy
from sqlalchemy import orm

from .db_session import SqlAlchemyBase


association_table = sqlalchemy.Table('groups_to_tests', SqlAlchemyBase.metadata,
    sqlalchemy.Column('group', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('groups.id')),
    sqlalchemy.Column('test', sqlalchemy.Integer,
                      sqlalchemy.ForeignKey('tests.id'))
)


class Test(SqlAlchemyBase):
    __tablename__ = 'tests'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    name = sqlalchemy.Column(sqlalchemy.String, nullable=False)
    description = sqlalchemy.Column(sqlalchemy.String, nullable=True)
    creator_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))

    creator = orm.relation("User")
    questions = orm.relation("Question", back_populates='test')
    statistics = orm.relation("Result", back_populates='test')
    groups = orm.relation("Group",
                          secondary="groups_to_tests",
                          backref="test")

    def __repr__(self):
        return f"<Test {self.id} {self.name}>"
