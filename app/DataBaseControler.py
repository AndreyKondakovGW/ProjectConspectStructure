from app import db
from app.models import User, ConspectDB, PhotoDB, Tag, ConspectTagRelation, FragmentDB, FragmentToTagRelations, FragmentsRelation, AccessDB
from app.UserDBAPI1 import get_user


def check_conspect_in_base(user: User, name: str):
    conspects = user.get_all_conspects()
    res = False
    for conspect in conspects:
        if conspect.name == name:
            res = True
    return res


def add_conspect(name, date, user_id):
    # TODO: настроить корректную работу с датой между питоном и sql
    conspect = ConspectDB(name=name, date=date)
    db.session.add(conspect)
    db.session.add(AccessDB(user_id=user_id, conspect_id=conspect.id))
    db.session.commit()


def add_photo(filename: str):
    photo = PhotoDB(filename=filename)
    db.session.add(photo)
    db.session.commit()
    return photo


def add_photo_to_conspect(photo: PhotoDB, conspect: ConspectDB):
    photo.id_conspect = conspect.id
    db.session.commit()


def set_photo_order(*_, first: PhotoDB, photoes: []):
    if not photoes:
        exit()
    else:
        first.set_next(photoes[0].id)
        photoes[0].set_pred(first.id)
        for i in range(1, len(photoes)-1):
            photoes[i].set_pred(photoes[i-1].id)
            photoes[i].set_next(photoes[i+1])
        photoes[-1].set_pred(photoes[-2])
        db.session.commit()


def add_all_photoes(names: [], conspect: ConspectDB):
    for name in names:
        photo = PhotoDB(filename=name, id_conspect=conspect.id)
        db.session.add(photo)
        db.session.commit()


# def all_user_concpects(user):
#    return user.get_all_conspects()


# def check_user_access(user: User, conspect: ConspectDB):
#    return AccessDB.check_access(user=user, conspect=conspect)


# находит в списке айдишников тот, у которого имя конспекта = name
def conspect_id_by_name(conspect_ids: [], name: str):
    res = None
    for id in conspect_ids:
        cname = ConspectDB.query.filter_by(id=id).first().name
        if cname == name:
            res = cname
            break
    return res


# выдаёт все фото конспекта
def get_conspect(*_, conspect: ConspectDB):
    if conspect.id is not None:
        return [photo for photo in PhotoDB.query.filter_by(id_conspect=conspect.id)]
    else:
        return []


def all_fragments_by_tag(tag: Tag):
    farr = FragmentDB.query.join(FragmentToTagRelations, FragmentDB.id == FragmentToTagRelations.fragment_id).\
                        filter(FragmentToTagRelations.tag_id == tag.id).all()
    return farr
