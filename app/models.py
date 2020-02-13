from app import Session
from app.__init__ import engine
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from app import db, login
from flask_login import UserMixin
import random

# ----------db section ----------------------------

ROLE_USER = 0
ROLE_ADMIN = 1
ID_VALUE = 1010
id_dict = {}


def gererate_id():
    return ID_VALUE + random.randint(1, 100)


# Демо версия класс пользователья которую потом надо будет реализовать
# через базу данных
class User(UserMixin):
    def __init__(self, nickname, password):
        self.id = str(gererate_id())
        self.nickname = nickname
        self.password = int(password)
        id_dict[self.id] = self.nickname

    def __repr__(self):
        return '<User %r>' % (self.nickname)


db['admin'] = User('admin', 123)


Base = declarative_base()  # описание таблицы пользователей вместе с классом пользователя
session = Session()  # создание объекта-сессии


# Класс пользователья с использованием базы данных скюл лайт
class UserDB(UserMixin, Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True)
    password = Column(String, nullable=False)

    def __init__(self, name, password):
        self.name = name
        self.password = password


    @staticmethod
    @login.user_loader
    def load_user(id):
        print(id)
        user = session.query(UserDB).filter_by(id=int(id)).first()
        return user

    def __repr__(self):
        return "<User('%s', '%s')>" % (self.name, self.password)


Base.metadata.create_all(engine)





session.add(UserDB('admin', str(123)))
session.commit()
# print(sessoion.query(UserDB).first())
# print(sessoion.query(UserDB).filter_by(name='admin').first())
# print(sessoion.query(UserDB).filter_by(name='admin1').first())
