from app import Session
from app.__init__ import engine
from sqlalchemy import Column, Integer, String, Date, create_engine
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


class ConspectsDB(Base):
    __tablename__ = "Conspects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    name = Column(String)

    def __init__(self, date, name):
        self.name = name
        self.date = date


class Tag(Base):
    __tablename__ = "Tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    user_id = Column(String, nullable=False)

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id


class ConspectTagRelation(Base):
    __tablename__ = "ConpectTagRelations"
    conspect_id = Column(Integer,nullable=False)
    tag_id = Column(Integer, nullable=False)

    def __init__(self, conspect_id, tag_id):
        self.conspect_id = conspect_id
        self.tag_id = tag_id


class PhotoDB(Base):
    __tablename__ = 'Photoes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, unique=True, nullable=False)
    id_pred = Column(Integer)
    id_next = Column(Integer)
    id_conspect = Column(Integer)

    def __init__(self, filename, predname, nextname, conspect_id):
        self.filename = filename
        self.id_pred = session.query(PhotoDB.id).filter_by(filename=predname)
        self.id_next = session.query(PhotoDB.id).filter_by(filename=nextname)
        self.id_conspect = conspect_id


class FragmentDB(Base):
    __tablename__ = "Fragments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    photo_id = Column(Integer, nullable=False)
    x1 = Column(Integer, nullable=False)
    y1 = Column(Integer, nullable=False)
    x2 = Column(Integer, nullable=False)
    y2 = Column(Integer, nullable=False)
    name = Column(String)

    def __init__(self, photo_id,*_, x1, y1, x2, y2):
        self.photo_id = photo_id
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

    def set_name(self, name):
        self.name = name


class FragmentsRelation(Base):
    __tablename__ = "FragmentsRelations"
    id_master = Column(Integer, nullable=False)
    id_slave = Column(Integer, nullable=False)

    def __init__(self, id_master, id_slave):
        self.id_master = id_master
        self.id_slave = id_slave


class FragmentToTagRelations(Base):
    __tablename__ = "FragmentToTagRelations"
    fragment_id = Column(Integer, nullable=False)
    tag_id = Column(Integer, nullable=False)

    def __init__(self, fragment_id, tag_id):
        if (not session.query(FragmentDB).filter_by(id=fragment_id).all()) or (not session.query(Tag).filter_by(id=tag_id).all()):
            print("Ошибка при создании отношения: не существует искомый тэг или искомый фрагмент")
            return
        else:
            self.fragment_id = fragment_id
            self.tag_id = tag_id


# session.add(UserDB('admin', str(123)))
# session.commit()