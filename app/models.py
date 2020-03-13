from app import Session
from app import engine
from sqlalchemy import Column, Integer, String, Date, ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint, create_engine
from sqlalchemy.ext.declarative import declarative_base
from app import db, login
from flask_login import UserMixin
import random

# ----------db section ----------------------------

ROLE_USER = 0
ROLE_ADMIN = 1
ID_VALUE = 1010
id_dict = {}


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

    def set_permission(self, conspect):
        acess = AccessDB(self.id, conspect.id)
        session.add(acess)

    def __repr__(self):
        return "<User('%s', '%s')>" % (self.name, self.password)


#Base.metadata.create_all(engine)


class ConspectDB(Base):
    __tablename__ = "Conspects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date)
    name = Column(String)

    def __init__(self, date, name):
        self.name = name
        self.date = date

    def set_date(self, date):
        self.date = date
        # изменения не будут закомичены

    def set_tag(self, tag):
        if tag in session:
            ctrelation = ConspectTagRelation(self.id, tag.id)
            session.add(ctrelation)
            session.commit()


class AccessDB(Base):
    __tablename__ = "Access"
    user_id = Column(Integer, nullable=False)
    conspect_id = Column(Integer, nullable=False)
    __table_args__ = (PrimaryKeyConstraint('user_id', 'conspect_id'),
                      ForeignKeyConstraint(['conspect_id'], ['Conspects.id']),
                      ForeignKeyConstraint(['user_id'], ['users.id']))

    def __init__(self, user_id, conspect_id):
        self.user_id = user_id
        self.conspect_id = conspect_id


class Tag(Base):
    __tablename__ = "Tags"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, unique=True, nullable=False)
    user_id = Column(String, nullable=False)

    def __init__(self, name, user_id):
        self.name = name
        self.user_id = user_id

    def rename(self, newname):
        self.name = newname
        # изменения не будут закомичены


#Base.metadata.create_all(engine)


class ConspectTagRelation(Base):
    __tablename__ = "ConspectTagRelations"
    conspect_id = Column(Integer, nullable=False)
    tag_id = Column(Integer, ForeignKey('Tags.id'), nullable=False)
    __table_args__ = (PrimaryKeyConstraint('conspect_id', 'tag_id'),
                      ForeignKeyConstraint(['conspect_id'], ['Conspects.id']),
                      ForeignKeyConstraint(['tag_id'], ['Tags.id']))

    def __init__(self, conspect_id, tag_id):
        self.conspect_id = conspect_id
        self.tag_id = tag_id


class PhotoDB(Base):
    __tablename__ = 'Photoes'
    id = Column(Integer, primary_key=True, autoincrement=True)
    filename = Column(String, unique=True, nullable=False)
    id_pred = Column(Integer)
    id_next = Column(Integer)
    id_conspect = Column(Integer, ForeignKey('Conspects.id'))

    def __init__(self, filename, predname, nextname, conspect_id):
        self.filename = filename
        self.id_pred = session.query(PhotoDB.id).filter_by(filename=predname)
        self.id_next = session.query(PhotoDB.id).filter_by(filename=nextname)
        self.id_conspect = conspect_id

    def set_next(self, id_next):
        self.id_next = id_next
        # незакомиченные изменения

    def set_pred(self, id_pred):
        self.id_pred = id_pred
        # незакомиченные изменения


class FragmentDB(Base):
    __tablename__ = "Fragments"
    id = Column(Integer, primary_key=True, autoincrement=True)
    photo_id = Column(Integer, ForeignKey('Photoes.id'), nullable=False)
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
        # незакомиченные изменения

    def set_tag(self, tag):
        if tag in session:
            ftrelation = FragmentToTagRelations(self.id, tag.id)
            session.add(ftrelation)
            session.commit()


class FragmentsRelation(Base):
    __tablename__ = "FragmentsRelations"
    id_master = Column(Integer, nullable=False)
    id_slave = Column(Integer, nullable=False)
    __table_args__ = (PrimaryKeyConstraint('id_master', 'id_slave'),
                      ForeignKeyConstraint(['id_master'], ['Fragments.id']),
                      ForeignKeyConstraint(['id_slave'], ['Fragments.id']))

    def __init__(self, id_master, id_slave):
        self.id_master = id_master
        self.id_slave = id_slave


class FragmentToTagRelations(Base):
    __tablename__ = "FragmentToTagRelations"
    fragment_id = Column(Integer, nullable=False)
    tag_id = Column(Integer, nullable=False)
    __table_args__ = (PrimaryKeyConstraint('fragment_id', 'tag_id'),
                      ForeignKeyConstraint(['fragment_id'], ['Fragments.id']),
                      ForeignKeyConstraint(['tag_id'], ['Tags.id']))

    def __init__(self, fragment_id, tag_id):
        if (not session.query(FragmentDB).filter_by(id=fragment_id).all()) or (not session.query(Tag).filter_by(id=tag_id).all()):
            print("Ошибка при создании отношения: не существует искомый тэг или искомый фрагмент")
            return
        else:
            self.fragment_id = fragment_id
            self.tag_id = tag_id


Base.metadata.create_all(engine)
# session.add(UserDB('admin', str(123)))
# session.commit()