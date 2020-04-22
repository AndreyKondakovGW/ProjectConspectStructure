from app.models import User, AccessDB, ConspectDB
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


# ----------------------sharing section--------------------------------

def check_access(user: User, conspect: ConspectDB):
    print(user.id)
    print(conspect.id)
    return AccessDB.check_access(user, conspect)


def add_access(user: User, conspect: ConspectDB):
    if user and conspect:
        access = AccessDB(user_id=user.id, conspect_id=conspect.id)
        db.session.add(access)
        db.session.commit()
    else:
        access = None
    return access
