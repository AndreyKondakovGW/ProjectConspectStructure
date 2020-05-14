import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://main:123@localhost:5432/test_database"
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    UPLOAD_FOLDER = basedir+'/static/Photo'
    ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SEND_FILE_MAX_AGE_DEFAULT = 0
