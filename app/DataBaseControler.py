from app import db
from app.models import User, ConspectDB, PhotoDB, Tag, ConspectTagRelation, FragmentDB, FragmentToTagRelations, FragmentsRelation, AccessDB
from app.UserDBAPI1 import get_user
from app.config import basedir
from app.pdf_creater import create_pdf_from_images


def check_conspect_in_base(user: User, name: str):
    conspects = user.get_all_conspects()
    res = False
    for conspect in conspects:
        if conspect.name == name:
            res = True
    return res


def add_conspect(name,  user: User):
    conspect = ConspectDB(name=name)
    db.session.add(conspect)
    db.session.commit()
    db.session.add(AccessDB(user_id=user.id, conspect_id=conspect.id))
    db.session.commit()
    return conspect


def add_photo(filename: str):
    photo = PhotoDB(filename=filename)
    db.session.add(photo)
    db.session.commit()
    return photo


def add_photo_to_conspect(photo: PhotoDB, conspect: ConspectDB):
    photo.id_conspect = conspect.id
    db.session.commit()


def get_photo_by_filename(filename: str):
    return PhotoDB.query.filter_by(filename=filename).first()


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


# находит в списке айдишников тот, у которого имя конспекта = name
def conspect_by_name(user: User, name: str):
    res = None
    conspects = user.get_all_conspects()
    for conspect in conspects:
        if conspect.name == name:
            res = conspect
            break
    return res


# выдаёт все фото конспекта
def get_conspect_photoes(*_, conspect: ConspectDB):
    if conspect.id is not None:
        return [photo.filename for photo in PhotoDB.query.filter_by(id_conspect=conspect.id)]
    else:
        return []


def create_pdf_conspect(user: User, conspect_name: str):
    conspect = conspect_by_name(user, conspect_name)
    photoes = [basedir + "/static/Photo/" + photoname for photoname in get_conspect_photoes(conspect=conspect)]
    pdf_name = conspect_name + '_' + user.name
    if photoes:
        create_pdf_from_images(pdf_name, photoes)
        return pdf_name+'.pdf'
    else:
        return ""


def add_fragment(user: User, photoname: str, *_, name=None, x1, y1, x2, y2):
    photo = get_photo_by_filename(photoname)
    if photo is not None:
        fragment = FragmentDB(photo_id=photo.id, x1=x1, x2=x2, y1=y1, y2=y2)
        if name:
            fragment.set_name(name)
        db.session.add(fragment)
        db.session.commit()
        return fragment
    else:
        return None


def all_fragments_by_tag(tag: Tag):
    farr = FragmentDB.query.join(FragmentToTagRelations, FragmentDB.id == FragmentToTagRelations.fragment_id).\
                        filter(FragmentToTagRelations.tag_id == tag.id).all()
    return farr
