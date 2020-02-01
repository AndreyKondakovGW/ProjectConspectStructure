from app import db
from app.models import User

def add_to_db(key,value):
    db[key] = User(key,value)


def right_user_data(key,value):
    if db:
        return db[key].password == int(value)
    else: return False


def show_all_user():
    if db:
        print(db)




