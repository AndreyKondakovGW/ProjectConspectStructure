from flask import Flask
from app.config import basedir
from app.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import basedir
from flask_sqlalchemy import SQLAlchemy
import os

# ----------configure section ---------------------
app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app) #объект, через который происходит работа с бд

DESKTOP_MODE = True

if DESKTOP_MODE:
    from webbrowser import open as webopen
    webopen(r'http://127.0.0.1:5000/')
    DESKTOP_MODE = False

# ---------LoginManagerSection-----------
from flask_login import LoginManager
login = LoginManager(app)
login.login_view = 'index'

#db = {}  # dict

from app import routes, models
