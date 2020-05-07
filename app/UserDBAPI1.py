from app.models import User, AccessDB, ConspectDB, Friendship
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


def user_by_id(id: int):
    return User.query.filter_by(id=id).first()

# ----------------------sharing section--------------------------------


def check_access(user: User, conspect: ConspectDB, status: str = "owner"):
    print(user.id)
    print(conspect.id)
    return AccessDB.check_access(user, conspect, status)


def add_access(user: User, conspect: ConspectDB, status: str):
    if user and conspect:
        access = AccessDB(user_id=user.id, conspect_id=conspect.id, status=status)
        db.session.add(access)
        db.session.commit()
    else:
        access = None
    return access


def add_to_friends(adder: User, adding: User):
    return adder.add_to_friends(adding.id)


def get_friends_list(user: User):
    return [user_by_id(friendship.user2_id) for friendship in Friendship.query.filter_by(user1_id=user.id).all()]


def search_for_user(search_input: str):
    users = User.query.filter(User.name.startswith(search_input)).all()
    return users


def get_users_conspects(cur_user: User, user: User):
    access_alias1 = db.aliased(AccessDB)
    access_alias2 = db.aliased(AccessDB)
    conspects = ConspectDB.query.join(access_alias1, access_alias1.conspect_id == ConspectDB.id)\
        .join(access_alias2, access_alias2.conspect_id == ConspectDB.id)\
        .filter(db.or_(db.and_(access_alias1.user_id == user.id, access_alias1.status == "owner"),
                       access_alias2.user_id == cur_user.id))\
        .filter(db.or_(ConspectDB.is_global, access_alias2.status == "view")).all()
    return conspects
