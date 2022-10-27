import sqlalchemy
from sqlalchemy import orm


from .db_session import SqlAlchemyBase


class User(SqlAlchemyBase):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer,
                           primary_key=True, autoincrement=True)
    telegram_username = sqlalchemy.Column(sqlalchemy.String)
    won = sqlalchemy.Column(sqlalchemy.Boolean, default=True)