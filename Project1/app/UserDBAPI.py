from app import db


def add_to_db(key,value):
    db[key] = value


def right_user_data(key,value):
    if db:
        print(db[key].password)
        print(value)
        return db[key].password == int(value)
    else: return False


def show_all_user():
    if db:
        print(db)




