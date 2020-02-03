from flask import Flask
from app.config import basedir
from app.config import Config
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import basedir
import os

# ----------db section ----------------------------

engine = create_engine('sqlite:///' + os.path.join(basedir, 'DB.db'),
                       convert_unicode=True)

Session = sessionmaker(bind=engine)

session = Session()

# ----------configure section ---------------------
app = Flask(__name__)
app.config.from_object(Config)

DESKTOP_MODE = True

if DESKTOP_MODE:
    from webbrowser import open as webopen
    webopen(r'http://127.0.0.1:5000/')

# ---------LoginManagerSection-----------
from flask_login import LoginManager
login = LoginManager(app)
login.login_view = 'index'

db = {}  # dict

from app import routes, models
