from app import Session
from app.models import session, UserDB
from app.models import ConspectDB, PhotoDB, Tag, ConspectTagRelation, FragmentDB, FragmentToTagRelations, FragmentsRelation, AccessDB
from app.UserDBAPI import get_user

# --------------sessions control--------------
# controlled_session = Session()
#
#
# def commit_decorator(wrapped_fun, flag, f_session):
#     def wrapper(self, *args, **kwargs):
#         wrapped_fun(self, *args, **kwargs)
#         f_session.commit()
#
#     if flag:
#         return wrapper
#     else:
#         return wrapped_fun
#
#
# def add_decorator(wrapped_fun, flag, f_session):
#     def wrapper(self, *args, **kwargs):
#         obj = wrapped_fun(self, *args, **kwargs)
#         f_session.add(obj)
#         return obj
#
#     if flag:
#         return wrapper
#     else:
#         return wrapped_fun
#
#
# class DBController:
#     commit_flag = True
#     add_flag = True
#
#     def __init__(self, db_session):
#         self.db_session = db_session
#
#     def commit(self, fun_to_decorate):
#         fun_to_decorate = commit_decorator(fun_to_decorate, self.commit_flag, self.db_session)


# Основные функции требующие реализацие в базе текущий код просто заглушки
# также требуется добавит больше функций для взоимодействия с базой
def check_conspect_in_base(name):
    ...


def add_conspect(name, date, user_id):
    # TODO: настроить корректную работу с датой между питоном и sql
    conspect = ConspectDB(name=name, date=date)
    session.add(conspect)
    session.add(AccessDB(user_id=user_id, conspect_id=conspect.id))


def add_photo_to_conspect(name, predname, nextname, conspectid):
    photo = PhotoDB(name=name, predname=predname, nextname=nextname, conspect_id=conspectid)
    session.add(photo)
    # TODO: загрузка фото на сервер
    print('пользователь загрузил фото', name, 'в базу')
    return photo


def all_user_concpects(user_id):
    return session.query(AccessDB.conspect_id).filter_by(user_id=user_id).all()


def check_user_access(user_id, conspect_id):
    return conspect_id in all_user_concpects(user_id)


# находит в списке айдишников тот, у которого имя конспекта = name
def conspect_id_by_name(conspect_ids, name):
    res = None
    for id in conspect_ids:
        cname = session.query(ConspectDB.name).filter_by(id=id).first()[0]
        if (cname==name):
            res = cname
            break
    return res


def get_conspect(name, conspect_name, username):
    user_id = get_user(username).id
    conspect_ids = all_user_concpects(user_id)
    conspect_id = conspect_id_by_name(conspect_ids, conspect_name)
    if conspect_id:
        fnames = [name for name in session.query(PhotoDB.filename).filter_by(id_conspect=conspect_id).all()]
    else:
        fnames = []
    return fnames
