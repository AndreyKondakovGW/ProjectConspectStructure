from app import db
from app.models import User
from app.models import UserDB
from app import session


def add_to_db(user):
    session.add(user)


def add_to_db(name, password):
    user = UserDB(name=name, password=password)
    add_to_db(user)


def user_exist(name):
    return name in session.query(UserDB.name)


# нетронутые заглушки
def right_user_data(key, value):
    if db:
        return db[key].password == int(value)
    else:
        return False


def show_all_user():
    if db:
        print(db)
