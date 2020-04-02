from app.models import UserDB
from app.models import session


def add_to_db_user(user):
    session.add(user)
    session.commit()


def add_to_db(name, password):
    user = UserDB(name=name, password=password)
    add_to_db_user(user)


def get_user(name):
    # print(session.query(UserDB).filter_by(name=name).first())
    return session.query(UserDB).filter_by(name=name).first()


def get_password(name):
    return session.query(UserDB.password).filter_by(name=name).first()[0]


def user_exist(name):
    print('проверим, есть ли пользователь')
    return len(session.query(UserDB).filter_by(name=name).all()) != 0


def check_password(name, password):
    pw = None
    if user_exist(name):
        pw = session.query(UserDB.password).filter_by(name=name).first()[0]
    return password == pw


def print_all_users():
    for user in session.query(UserDB).all():
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
