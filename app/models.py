from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint
from app import db
from app import login
from flask_login import UserMixin
import random

# ----------db section ----------------------------

ROLE_USER = 0
ROLE_ADMIN = 1
ID_VALUE = 1010
id_dict = {}



class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True)
    password = db.Column(db.String, nullable=False)

    @staticmethod
    @login.user_loader
    def load_user(id):
        print(id)
        user = User.query.filter_by(id=id).first()
        return user

    def __repr__(self):
        return "<User('%s', '%s')>" % (self.name, self.password)


class ConspectDB(db.Model):
    __tablename__ = "conspects"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date)
    name = db.Column(db.String)

    def set_date(self, date):
        self.date = date
        # изменения не будут закомичены

    def set_tag(self, tag):
        if tag in Tag.query.filter_by(id=tag.id):
            ctrelation = ConspectTagRelation(conspect_id=self.id, tag_id=tag.id)
            db.session.add(ctrelation)
            db.session.commit()


class AccessDB(db.Model):
    __tablename__ = "accesses"
    user_id = db.Column(db.Integer, nullable=False)
    conspect_id = db.Column(db.Integer, nullable=False)
    __table_args__ = (PrimaryKeyConstraint('user_id', 'conspect_id'),
                      ForeignKeyConstraint(['conspect_id'], ['conspects.id']),
                      ForeignKeyConstraint(['user_id'], ['users.id']))


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True, nullable=False)
    user_id = db.Column(db.String, nullable=False)

    def rename(self, newname):
        self.name = newname
        # изменения не будут закомичены


class ConspectTagRelation(db.Model):
    __tablename__ = "conspect_tag_relations"
    conspect_id = db.Column(db.Integer, nullable=False)
    tag_id = db.Column(db.Integer, db.ForeignKey('tags.id'), nullable=False)
    __table_args__ = (PrimaryKeyConstraint('conspect_id', 'tag_id'),
                      ForeignKeyConstraint(['conspect_id'], ['conspects.id']),
                      ForeignKeyConstraint(['tag_id'], ['tags.id']))


class PhotoDB(db.Model):
    __tablename__ = 'photoes'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    filename = db.Column(db.String, unique=True, nullable=False)
    id_pred = db.Column(db.Integer)
    id_next = db.Column(db.Integer)
    id_conspect = db.Column(db.Integer, db.ForeignKey('conspects.id'))

    def set_next(self, id_next):
        self.id_next = id_next
        # незакомиченные изменения

    def set_pred(self, id_pred):
        self.id_pred = id_pred
        # незакомиченные изменения


class FragmentDB(db.Model):
    __tablename__ = "fragments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photoes.id'), nullable=False)
    x1 = db.Column(db.Integer, nullable=False)
    y1 = db.Column(db.Integer, nullable=False)
    x2 = db.Column(db.Integer, nullable=False)
    y2 = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String)

    def set_name(self, name):
        self.name = name
        # незакомиченные изменения

    def set_tag(self, tag):
        if tag in Tag.query.filter_by(id=tag.id):
            ftrelation = FragmentToTagRelations(self.id, tag.id)
            db.session.add(ftrelation)
            db.session.commit()


class FragmentsRelation(db.Model):
    __tablename__ = "fragments_relations"
    id_master = db.Column(db.Integer, nullable=False)
    id_slave = db.Column(db.Integer, nullable=False)
    __table_args__ = (PrimaryKeyConstraint('id_master', 'id_slave'),
                      ForeignKeyConstraint(['id_master'], ['fragments.id']),
                      ForeignKeyConstraint(['id_slave'], ['fragments.id']))


class FragmentToTagRelations(db.Model):
    __tablename__ = "fragment_to_tag_relations"
    fragment_id = db.Column(db.Integer, nullable=False)
    tag_id = db.Column(db.Integer, nullable=False)
    __table_args__ = (PrimaryKeyConstraint('fragment_id', 'tag_id'),
                      ForeignKeyConstraint(['fragment_id'], ['fragments.id']),
                      ForeignKeyConstraint(['tag_id'], ['tags.id']))


db.create_all()