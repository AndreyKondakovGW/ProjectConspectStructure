import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config():
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    #SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:123@localhost:5432/postgres"
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
    UPLOAD_FOLDER = '/home/andrew/Документы/Flask/Project1/app/static/upload'
    ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
    SQLALCHEMY_TRACK_MODIFICATIONS = False