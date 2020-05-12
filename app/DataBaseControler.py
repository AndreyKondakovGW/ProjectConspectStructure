from app import db, app
from app.models import User, ConspectDB, PhotoDB, Tag, ConspectTagRelation, FragmentDB, FragmentToTagRelations, FragmentsRelation, AccessDB
from app.UserDBAPI1 import get_user
from app.config import basedir
from app.pdf_creater import create_pdf_from_images, cut
from app.pdf_creater import save_copy, filename_gen
import re


def check_conspect_in_base(user: User, name: str):
    return len(ConspectDB.query.join(AccessDB, ConspectDB.id == AccessDB.conspect_id).filter(AccessDB.user_id == user.id)
                .filter(db.or_(AccessDB.status == "owner", AccessDB.status == "redactor"))
                .filter(ConspectDB.name == name).all()) > 0


def conspect_by_id(id: int):
    return ConspectDB.query.filter_by(id=id).first()


def delete_conspect_by_id(id: int):
    conspect = conspect_by_id(id)
    db.session.delete(conspect)
    db.session.commit()


def add_conspect(name,  user: User, status: str = "owner", is_global: bool = True):
    conspect = ConspectDB(name=name, is_global=is_global)
    db.session.add(conspect)
    db.session.commit()
    db.session.add(AccessDB(user_id=user.id, conspect_id=conspect.id, status=status))
    db.session.commit()
    return conspect


def add_photo(filename: str):
    photo = PhotoDB(filename=filename)
    db.session.add(photo)
    db.session.commit()
    return photo


def delete_photo_db(photo: PhotoDB):
    db.session.delete(photo)
    db.session.commit()


def remove_from_conspect(photo: PhotoDB):
    photo.id_conspect = None
    db.session.commit()


def add_photo_to_conspect(photo: PhotoDB, conspect: ConspectDB):
    photo.id_conspect = conspect.id
    db.session.commit()


def get_photo_by_filename(filename: str):
    return PhotoDB.query.filter_by(filename=filename).first()


def photo_by_id(id: int):
    return PhotoDB.query.filter_by(id=id).first()


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
    conspect = ConspectDB.query.join(AccessDB, ConspectDB.id == AccessDB.conspect_id).filter(AccessDB.user_id == user.id)\
                        .filter(db.or_(AccessDB.status == "owner", AccessDB.status == "redactor"))\
                        .filter(ConspectDB.name == name).first()
    return conspect


def conspect_by_id(id: int):
    return ConspectDB.query.filter_by(id=id).first()


# выдаёт все фото конспекта
def get_conspect_photoes(conspect: ConspectDB):
    if conspect is not None:
        return PhotoDB.query.filter_by(id_conspect=conspect.id).all()
    else:
        return []


def create_pdf_conspect(user: User, id: int):
    conspect = conspect_by_id(id)
    photoes = [basedir + "/static/Photo/users/" + photo.filename for photo in get_conspect_photoes(conspect=conspect)]
    pdf_name = 'pdfs/conspect_' + user.name
    if photoes:
        create_pdf_from_images(pdf_name, photoes)
        return pdf_name+'.pdf'
    else:
        return ""


def all_photo_fragments(photo: PhotoDB):
    fragments = FragmentDB.query.filter_by(photo_id=photo.id).all()
    return fragments


def delete_conspect_from_db(conspect: ConspectDB):
    try:
        accesses = AccessDB.query.filter_by(conspect_id=conspect.id).all()
        for access in accesses:
            db.session.delete(access)
        db.session.commit()
        db.session.delete(conspect)
        db.session.commit()
        print("we are here")
    except Exception as e:
        print(e)
        db.session.rollback()
        print("rolling back")


# -----------------------fragments-tags-section----------------

def tag_by_name(user: User, name: str):
    tag_arr = user.get_all_tags()
    for tag in tag_arr:
        if tag.name == name:
            return tag
    return None


def tag_by_id(id: int):
    return Tag.query.filter_by(id=id).first()


def add_tag(user: User, name: str):
    tag = Tag(name=name, user_id=user.id)
    db.session.add(tag)
    db.session.commit()
    return tag


def add_fragment(user: User, photo: PhotoDB, *_, name=None, x1, y1, x2, y2):
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


def pdf_fragments_by_tag(user: User, tagname: str):
    tag = tag_by_name(user, tagname)
    if tag:
        farr = all_fragments_by_tag(tag)
        filenames = list()
        for i in range(0, len(farr)):
            photo = PhotoDB.query.filter_by(id=farr[i].photo_id).first()
            filename = basedir+"/static/Photo/pdfs/"+user.name+"_fragment_"+str(i+1)+'.png'
            cut("users/"+photo.filename, farr[i].x1, farr[i].y1, farr[i].x2, farr[i].y2, filename)
            filenames.append(filename)
        name = "pdfs/"+user.name+"_set"
        create_pdf_from_images(name, filenames)
        return name+".pdf"
    else:
        return ""


def all_fragment_relations_with_fragment(fragment: FragmentDB):
    fragment_relations = FragmentsRelation.query\
            .filter((FragmentsRelation.id_master == fragment.id) or (FragmentsRelation.id_slave == fragment.id)).all()
    return fragment_relations


def all_tag_relations_with_fragment(fragment: FragmentDB):
    tag_relations = FragmentToTagRelations.query.filter_by(fragment_id=fragment.id).all()
    return tag_relations


def all_tags_by_fragment(fragment: FragmentDB):
    relations = all_tag_relations_with_fragment(fragment)
    tags = [tag_by_id(relation.tag_id) if relation.tag_id is not None else None for relation in relations]
    return tags


def delete_fragment(fragment: FragmentDB):
    fragment_relations = all_fragment_relations_with_fragment(fragment)
    tag_relations = all_tag_relations_with_fragment(fragment)
    is_deleted = True
    try:
        if tag_relations:
            for tr in tag_relations:
                db.session.delete(tr)
        if fragment_relations:
            for fr in fragment_relations:
                db.session.delete(fr)
        db.session.commit()
        db.session.delete(fragment)
        db.session.commit()
        print("deleted fragment"+str(fragment.id))
    except Exception as e:
        print(e)
        is_deleted = False
        db.session.rollback()
    return is_deleted


def delete_photo_with_fragments(photo: PhotoDB):
    fragments = all_photo_fragments(photo)
    success = True
    for fragment in fragments:
        tagarr = all_tags_by_fragment(fragment)
        is_deleted = delete_fragment(fragment)
        if not is_deleted:
            success = False
            break
        for tag in tagarr:
            if not all_fragments_by_tag(tag):
                try:
                    db.session.delete(tag)
                    db.session.commit()
                except Exception as e:
                    db.session.rollback()
                    print(e)
    if success:
        db.session.delete(photo)
        db.session.commit()
    return success


def query_conrtoller(user: User, string: str):
    union_strings = re.split(r'\s\|\s', string)
    ids_set = set()
    for union_str in union_strings:
        print(union_str)
        tag_strings = [s[1:-2].strip() if s and len(s) > 2 else "" for s in re.split(r'\s&\s', union_str)]
        tag_ids_set = set()
        for tag_name in tag_strings:
            print(tag_name)
            tag = Tag.query.filter_by(user_id=user.id).filter_by(name=tag_name).first()
            if tag:
                tag_ids_set.add(tag.id)
        conditions = [FragmentToTagRelations.tag_id == tag_id for tag_id in tag_ids_set]
        query = db.session.query(FragmentToTagRelations.fragment_id.label('fragment_id'),
                                 db.func.count(FragmentToTagRelations.fragment_id).label('match_count'))\
            .filter(db.or_(*conditions)).group_by(FragmentToTagRelations.fragment_id)
        found_records = query.cte()
        fragment_ids = db.session.query(found_records.c.fragment_id)\
            .filter(found_records.c.match_count == len(conditions)).all()
        ids_set = ids_set.union(fragment_ids)
    return [FragmentDB.query.filter_by(id=fr_id).first() for fr_id in sorted(ids_set)]


def pdf_fragments_by_fragments_arr(user: User, fragments: [FragmentDB]):
    print("fragments is not empty")
    filenames = list()
    i = 0
    for fragment in fragments:
        photo = PhotoDB.query.filter_by(id=fragment.photo_id).first()
        filename = basedir+"/static/Photo/pdfs/"+user.name+"_fragment_"+str(i)+'.png'
        cut("users/"+photo.filename, fragment.x1, fragment.y1, fragment.x2, fragment.y2, filename)
        filenames.append(filename)
        i += 1
    name = "pdfs/"+user.name+"_set"
    create_pdf_from_images(name, filenames)
    return name+".pdf"


def copy_conspect(user: User, conspect: ConspectDB):
    photos = get_conspect_photoes(conspect)
    success = True
    try:
        conspect1 = add_conspect(conspect.name, user, "owner", is_global=False)
        for photo in photos:
            path = app.config['UPLOAD_FOLDER'] + '/users/' + user.name
            image_path = app.config['UPLOAD_FOLDER'] + '/users/' + photo.filename
            copy_name = filename_gen(path, photo.filename)
            save_copy(image_path, copy_name)
            copy_name = copy_name.split('/')[-1]
            photo_copy = PhotoDB(filename=user.name + '/' + copy_name, id_conspect=conspect1.id)
            db.session.add(photo_copy)
        db.session.commit()
    except Exception as e:
        print(e)
        db.session.rollback()
        success = False
    return success


def save_tags_as_tag(user: User, tags: [Tag], new_tag_name: str):
    conds = [(FragmentToTagRelations.tag_id == tag.id) for tag in tags]
    fragments = FragmentDB.query.join(FragmentToTagRelations, FragmentToTagRelations.fragment_id == FragmentDB.id).\
        filter(db.or_(*conds)).all()
    new_tag = Tag(name=new_tag_name, user_id=user.id)
    db.session.add(new_tag)
    db.session.commit()
    try:
        for fragment in fragments:
            fragnent_to_tag_relation = FragmentToTagRelations(fragment_id=fragment.id, tag_id=new_tag.id)
            db.session.add(fragnent_to_tag_relation)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        db.session.delete(new_tag)
        db.session.commit()
        print(e)
        return False
    return True
