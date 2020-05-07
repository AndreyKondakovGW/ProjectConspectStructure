from sqlalchemy import PrimaryKeyConstraint, ForeignKeyConstraint
from app import db
from app import login_manager
from flask_login import UserMixin
import random

# ----------костыль для редактора----------------
filename = "American_Beaver.jpg"

# ----------db section ----------------------------


class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, unique=True)
    password = db.Column(db.String, nullable=False)

    @staticmethod
    @login_manager.user_loader
    def load_user(id):
        user = User.query.filter_by(id=id).first()
        return user

    def __repr__(self):
        return "<User('%s', '%s')>" % (self.name, self.password)

    def get_all_conspects(self):
        # сложный запрос с join
        conspect_arr = ConspectDB.query.join(AccessDB, ConspectDB.id == AccessDB.conspect_id)\
                        .filter(AccessDB.user_id == self.id)\
                        .filter(db.or_(AccessDB.status == "owner", AccessDB.status == "redactor")).all()
        # conspect_ids = [access.conspect_id for access in AccessDB.query.filter_by(user_id=self.id).all()]
        # conspect_arr = [ConspectDB.query.filter_by(id=conspect_id).first() for conspect_id in conspect_ids]
        return conspect_arr

    def get_all_tags(self):
        return Tag.query.filter_by(user_id=self.id).all()

    def add_to_friends(self, user_id):
        success = True
        if self.id == user_id:
            return False
        try:
            friendship = Friendship(user1_id=self.id, user2_id=user_id)
            db.session.add(friendship)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            success = False
        return success


class ConspectDB(db.Model):
    __tablename__ = "conspects"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    date = db.Column(db.Date)
    name = db.Column(db.String, unique=True)
    is_global = db.Column(db.Boolean, nullable=False)

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
    status = db.Column(db.String, nullable=False)
    __table_args__ = (PrimaryKeyConstraint('user_id', 'conspect_id'),
                      ForeignKeyConstraint(['conspect_id'], ['conspects.id']),
                      ForeignKeyConstraint(['user_id'], ['users.id']))

    @staticmethod
    def check_access(user: User, conspect: ConspectDB, status: str = "owner"):
        if not user:
            return False
        if not conspect:
            return False
        return AccessDB.query.filter_by(conspect_id=conspect.id).filter_by(user_id=user.id).first().status == status


class Tag(db.Model):
    __tablename__ = "tags"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

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
    filename = db.Column(db.String, nullable=False)
    id_pred = db.Column(db.Integer)
    id_next = db.Column(db.Integer)
    id_conspect = db.Column(db.Integer, db.ForeignKey('conspects.id'))

    def set_next(self, id_next):
        self.id_next = id_next
        # незакомиченные изменения

    def set_pred(self, id_pred):
        self.id_pred = id_pred
        # незакомиченные изменения

    def next(self):
        return PhotoDB.query.filter_by(id=self.id_next).first()

    def pred(self):
        return PhotoDB.query.filter_by(id=self.id_pred).first()


class FragmentDB(db.Model):
    __tablename__ = "fragments"
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    photo_id = db.Column(db.Integer, db.ForeignKey('photoes.id'), nullable=False)
    x1 = db.Column(db.Float, nullable=False)
    y1 = db.Column(db.Float, nullable=False)
    x2 = db.Column(db.Float, nullable=False)
    y2 = db.Column(db.Float, nullable=False)
    name = db.Column(db.String)

    def set_name(self, name):
        self.name = name
        # незакомиченные изменения

    def set_tag(self, tag):
        if tag in Tag.query.filter_by(id=tag.id):
            ftrelation = FragmentToTagRelations(fragment_id=self.id, tag_id=tag.id)
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


class Friendship(db.Model):
    __tablename__ = "friendship"
    user1_id = db.Column(db.Integer, nullable=False)
    user2_id = db.Column(db.Integer, nullable=False)
    __table_args__ = (PrimaryKeyConstraint('user1_id', 'user2_id'),
                      ForeignKeyConstraint(['user1_id'], ['users.id']),
                      ForeignKeyConstraint(['user2_id'], ['users.id']))


db.create_all()


# ----------------------default photo object---------------------------
# default_photo = PhotoDB(filename="American_Beaver.jpg")
# db.session.add(default_photo)
# db.session.commit()
default_photo = PhotoDB.query.filter_by(id=71).first()
