from app.models import session, UserDB
from app.models import ConspectsDB, PhotoDB, Tag, ConspectTagRelation, FragmentDB, FragmentToTagRelations, FragmentsRelation, AccessDB
from app.UserDBAPI import get_user

# Основные функции требующие реализацие в базе текущий код просто заглушки
# также требуется добавит больше функций для взоимодействия с базой
def check_conspect_in_base(name):
    ...


def add_conspect(name, date, user_id):
    # TODO: настроить корректную работу с датой между питоном и sql
    conspect = ConspectsDB(name=name, date=date)
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
        cname = session.query(ConspectsDB.name).filter_by(id=id).first()[0]
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
