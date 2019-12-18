from flask import Flask
from app.config import basedir
from app.config import Config
from app.models import User

# ----------db section ----------------------------
import sqlite3
# ---------LoginManagerSection-----------
from flask_login import LoginManager

app = Flask(__name__)
#app.config.from_object('config')

# ----------db section ----------------------------
from app import DBStarter
db={} #dict
db['admin'] = User('admin',123)
current_user=''

# ---------LoginManagerSection-----------

login = LoginManager(app)
app.config.from_object(Config)

from app import routes
