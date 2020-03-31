from app.models import User
from app import db


def add_to_db_user(user):
    db.session.add(user)
    db.session.commit()


def add_to_db(name, password):
    user = User(name=name, password=password)
    add_to_db_user(user)


def get_user(name):
    # print(session.query(UserDB).filter_by(name=name).first())
    return User.query.filter_by(name=name).first()


def get_password(name):
    user = User.query.filter_by(name=name).first()
    return user.password


def user_exist(name):
    print('проверим, есть ли пользователь')
    return len(User.query.filter_by(name=name).all()) != 0


def check_password(name, password):
    pw = None
    if user_exist(name):
        pw = get_password(name=name)
    return password == pw


def print_all_users():
    for user in User.query.all():
        print(user)


# нетронутые заглушки
def right_user_data(key, value):
    if db:
        return db[key].password == int(value)
    else:
        return False


def show_all_user():
    if db:
        print(db)
