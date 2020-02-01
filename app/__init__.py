from flask import Flask
from app.config import basedir
from app.config import Config
from  app.DataBase import Session

# ----------db section ----------------------------

app = Flask(__name__)
app.config.from_object(Config)

# ---------LoginManagerSection-----------
from flask_login import LoginManager
login = LoginManager(app)
login.login_view = 'index'

sessoion=Session()
db={} #dict

from app import routes,models
