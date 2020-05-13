# Основной скрипт сайта задаёт как сайт будет отвечать на те или иные
#  запросы пользователя
from app import app
from flask import render_template, flash, redirect, url_for, session, request, jsonify, send_file, abort
from app.forms import LoginForm, RegistrationForm, RedactorForm
from app.UserDBAPI1 import *
from app.config import Config, basedir
from app.DataBaseControler import *
from flask_login import current_user, login_user, logout_user, login_required
from app import login_manager
from werkzeug.urls import url_parse
from werkzeug.utils import secure_filename
from app.pdf_creater import filename_gen, create_pdf_from_images, cut
from app.models import filename, default_photo, AccessDB
import os


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    Lform = LoginForm()
    if Lform.submit1.data and Lform.validate():
        login(Lform)
    if current_user.is_authenticated:
        print('пользователь', current_user, 'вошёл в сеть')
        return redirect(url_for('main', username=current_user.name))
    return render_template('signin.html', Lform=Lform)


@app.route('/registrate', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    Rform = RegistrationForm()
    if Rform.submit2.data and Rform.validate():
        print('начата регистрация')
        add_to_db(name= Rform.username.data, password=Rform.password.data)
        return TryLoginUser( Rform.username.data,  Rform.password.data, Rform.remember_me.data)
    return render_template('registrate.html', Rform=Rform)


@app.route('/login', methods=['GET', 'POST'])
def login(form):
    print('login')
    print(form.username.data, form.password.data)
    return TryLoginUser(form.username.data, form.password.data, form.remember_me.data)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    print('пользователь', current_user, 'вышел из сети')
    logout_user()
    login_manager.unauthorized()
    return redirect(url_for('index'))


def TryLoginUser(name, password, remember_me):
    if user_exist(name):
        print('пользователь существует')
        if check_password(name, password):
            user = get_user(name)
            login_user(user, remember=remember_me)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
        else:
            print('введён пароль', password)
            pw = get_password(name)
            print('Пользователь', name, 'имеет другой пароль', pw)
            return redirect(url_for('index'))
    else:
        print('пользователь не существует')
        return redirect(url_for('index'))


@app.route('/get_current_user', methods=['GET'])
@login_required
def get_current_user():
    return jsonify({"id": current_user.id, "name": current_user.name})


# выдаёт список конспектов пользователя в виде JSON-массива
@app.route('/getconspects', methods=['GET'])
@login_required
def get_conspects():
    """return all user's conspects in JSON - list of dicts with 'id' and 'name' keys"""
    user = current_user
    conspects = user.get_all_conspects()
    jsonlist = list()
    for conspect in conspects:
        jsonlist.append({"id": conspect.id, "name": conspect.name, "is_global": conspect.is_global})
    return jsonify(jsonlist)


@app.route('/gettags', methods=['GET'])
@login_required
def get_tags():
    """return all user's tags in JSON - list of dicts with 'id' and 'name' keys"""
    user = current_user
    tags = user.get_all_tags()
    jsonlist = list()
    for tag in tags:
        jsonlist.append({"id": tag.id, "name": tag.name})
    return jsonify(jsonlist)


@app.route('/gettagpdf/<string:tagname>')
@login_required
def get_tag_pdf(tagname:str):
    print(tagname)
    """return pdf-file created from fragments with tag by name of tag"""
    pdf_name = basedir+'/static/Photo/'+pdf_fragments_by_tag(current_user, tagname)
    return send_file(pdf_name, mimetype='application/pdf')


@app.route('/getconspectphotos/<int:id>', methods=['GET'])
@login_required
def get_conspect_photos(id: int):
    """return all photoes in conspects (only information about photoes, not files themself"""
    user = current_user
    conspect = conspect_by_id(id)
    if not conspect:
        abort(404)
    if not (check_any_access(user, conspect) or conspect.is_global):
        abort(403)
    jsonlist = list()
    if conspect:
        photoes = get_conspect_photoes(conspect)
        for photo in photoes:
            dict = {"id": photo.id, "filename": photo.filename}
            jsonlist.append(dict)
    return jsonify(jsonlist)


@app.route('/getphotobyid/<int:id>')
@login_required
def get_photo_by_id(id: int):
    """return photo-file by photo id"""
    photo = photo_by_id(id)
    conspect = conspect_by_id(photo.id_conspect)
    if not (check_any_access(current_user, conspect) or conspect.is_global):
        abort(403)
    return send_file('static/Photo/users/'+photo.filename, mimetype='image')


@app.route('/getconspectpdf/<int:id>')
@login_required
def get_conspect_pdf(id: int):
    conspect = conspect_by_id(id)
    if not check_any_access(current_user, conspect):
        abort(403)
    pdf_name = create_pdf_conspect(current_user, id)
    if pdf_name:
        pdf_name = "static/Photo/"+pdf_name
    else:
        abort(404)
    return send_file(pdf_name, mimetype='application/pdf')


@app.route('/put_conspect/<string:conspectname>/<is_global>', methods=['PUT'])
@login_required
def put_conspect(conspectname: str, is_global: str):
    user = current_user
    is_global = is_global == "True"
    if not check_conspect_in_base(user, conspectname):
        conspect = add_conspect(conspectname, user, is_global=is_global)
    else:
        conspect = conspect_by_name(user, conspectname)
    return jsonify({"conspect_id": conspect.id, "conspect_name": conspectname, "is_global": conspect.is_global})


@app.route('/savephoto/<int:conspectid>', methods=['POST'])
@login_required
def save_conspect_photo(conspectid: int):
    conspect = conspect_by_id(conspectid)
    if not (check_access(current_user, conspect, "owner") or check_access(current_user, conspect, "redactor")):
        abort(403)
    photo = uploads(conspect)
    if photo is None:
        abort(400)
        photo = default_photo
    # session['redactorfoto_id'] = photo.id
    return jsonify({"id": photo.id, "filename": photo.filename, "id_conspect": photo.id_conspect})


def uploads(conspect: ConspectDB):
    file = request.files['file']
    if file and allowed_file(file.filename):
        path = app.config['UPLOAD_FOLDER']+'/users/'+current_user.name
        if not(os.path.exists(path)):
            os.mkdir(path)
        filename1 = filename_gen(path, secure_filename(file.filename))
        file.save(filename1)
        filename1 = filename1.split('/')[-1]
        photo = add_photo(current_user.name+'/'+filename1)
        if conspect:
            add_photo_to_conspect(photo=photo, conspect=conspect)
        return photo
    return None


@app.route('/deletephoto/<int:id>', methods=['DELETE'])
@login_required
def delete_photo(id: int):
    photo = photo_by_id(id)
    conspect = conspect_by_id(photo.id_conspect)
    if check_access(current_user, conspect, "owner") or check_access(current_user, conspect, "redactor"):
        fragments = all_photo_fragments(photo)
        if fragments:
            remove_from_conspect(photo)
        else:
            path = app.config['UPLOAD_FOLDER']+'/users/'+photo.filename
            delete_photo_db(photo)
            os.remove(path)


@app.route('/related_tags/<int:conspect_id>', methods=['GET'])
def get_related_tags(conspect_id: int):
    conspect = conspect_by_id(conspect_id)
    photoes = get_conspect_photoes(conspect)
    tags = set()
    for photo in photoes:
        for fragment in all_photo_fragments(photo):
            for tag in all_tags_by_fragment(fragment):
                if tag:
                    tags.add(tag)
    json = list()
    for tag in tags:
        json.append({"tag_id": tag.id, "tag_name": tag.name})
    return jsonify(json)


@app.route('/deleteconspect/<int:id>', methods=['DELETE'])
@login_required
def delete_conspect(id: int):
    conspect = conspect_by_id(id)
    if not check_access(current_user, conspect, "owner"):
        abort(403)
    for photo in get_conspect_photoes(conspect):
        path = app.config['UPLOAD_FOLDER'] +'/users/' + photo.filename
        success = delete_photo_with_fragments(photo)
        if success:
            if os.path.exists(path):
                os.remove(path)
            print("removed photo")
    delete_conspect_from_db(conspect=conspect)
    return "Deleted"


@app.route("/sendfragment", methods=['POST'])
@login_required
def post_fragment():
    user = current_user
    data = request.get_json()
    print(data)
    photo_id = data.get("photo_id")
    if photo_id:
        photo = photo_by_id(photo_id)
    else:
        photo = default_photo
    x1 = int(data.get("x1"))/100
    y1 = int(data.get("y1"))/100
    x2 = int(data.get("x2"))/100
    y2 = int(data.get("y2"))/100
    if not ((x2-x1 != 0) and (y2-y1 != 0)):
        x1, y1 = 0, 0
        x2, y2 = 1, 1
    fragment = add_fragment(user, photo, x1=x1, y1=y1, x2=x2, y2=y2)
    tags = data.get("tags")
    if tags:
        for t in tags:
            tag = tag_by_name(user, t)
            if not tag:
                tag = add_tag(user, t)
            fragment.set_tag(tag)
    return jsonify({"fragment_id": fragment.id})


@app.route('/add_friend/<int:friend_id>', methods=['POST'])
@login_required
def add_friend(friend_id: int):
    user = current_user
    adding_succes = user.add_to_friends(friend_id)
    return str(adding_succes)


@app.route('/delete_friend/<int:friend_id>', methods=['DELETE'])
@login_required
def delete_friend(friend_id: int):
    user = user_by_id(friend_id)
    if not remove_from_friends(current_user, user):
        abort(520)
    return "Deleted"


@app.route('/friend_list', methods=['GET'])
@login_required
def friend_list():
    user = current_user
    friends = get_friends_list(user)
    jsonlist = list()
    for friend in friends:
        jsonlist.append({"user_id": friend.id, "username": friend.name})
    return jsonify(jsonlist)


@app.route('/search_users/<string:search>', methods=['GET'])
@login_required
def search_users(search: str):
    users = search_for_user(search)
    json_list = list()
    for user in users:
        if user.id != current_user.id:
            json_list.append({"user_id": user.id, "username": user.name})
    return jsonify(json_list)


@app.route('/get_opened_conspects/<int:user_id>', methods=['GET'])
@login_required
def get_opened_conspects( user_id: int):
    cur_user = current_user
    user = user_by_id(user_id)
    conspects = get_users_conspects(cur_user, user)
    if not conspects:
        return jsonify([])
    else:
        return jsonify([{"id": conspect.id, "name": conspect.name} for conspect in conspects])


@app.route('/share_conspect/<int:conspect_id>/<int:user_id>/<string:status>', methods=['POST'])
@login_required
def share_conspect(conspect_id: int, user_id: int, status: str = "viewer"):
    conspect = conspect_by_id(conspect_id)
    if AccessDB.check_access(current_user, conspect):
        user = user_by_id(user_id)
        access = add_access(user, conspect, status)
        if access:
            return "success"
        else:
            abort(520)
            return "error"
    else:
        abort(403)
        return "error"


@app.route('/remove_user_access/<int:user_id>/<int:conspect_id>', methods=['DELETE'])
@login_required
def remove_user_access(user_id: int, conspect_id: int):
    conspect = conspect_by_id(conspect_id)
    if not check_access(current_user, conspect, "owner"):
        abort(403)
    user = user_by_id(user_id)
    if remove_access(user, conspect):
        return "success"
    else:
        abort(520)
        return "error"


@app.route('/share_conspect_to_friends/<int:id>/<status>', methods=['POST'])
@login_required
def share_conspect_to_friends(id: int, status="viewer"):
    if not status:
        status = "viewer"
    if not is_correct_status(status):
        abort(400)
        return "error"
    f_list = get_friends_list(current_user)
    conspect = conspect_by_id(id)
    for friend in f_list:
        if not check_any_access(friend, conspect):
            add_access(friend, conspect, status)
    return "success"


@app.route('/share_conspect_to_all/<int:id>', methods=['PUT'])
@login_required
def share_conspect_to_all(id: int):
    conspect = conspect_by_id(id)
    if check_access(current_user, conspect, "owner"):
        share_to_all(conspect)
    else:
        abort(403)
    return "success"


@app.route('/set_conspect_private/<int:id>', methods=['PUT'])
@login_required
def set_private(id: int):
    conspect = conspect_by_id(id)
    if check_access(current_user, conspect, "owner"):
        conspect.is_global = False
    else:
        abort(403)
    return "success"


@app.route('/get_is_global/<int:id>', methods=['GET'])
@login_required
def get_is_global(id: int):
    conspect = conspect_by_id(id)
    if not conspect:
        abort(404)
    return jsonify({"is_global": str(conspect.is_global)})


@app.route('/get_users_with_access/<int:conspect_id>', methods=['GET'])
@login_required
def get_users_with_access(conspect_id: int):
    conspect = conspect_by_id(conspect_id)
    if not check_access(current_user, conspect, "owner"):
        abort(403)
    users_json = list()
    users_json.append({"user_id": -1, "username": str(conspect.is_global)})
    for user in users_with_access(conspect):
        if user.id != current_user.id:
            users_json.append({"user_id": user.id, "username": user.name})
    return jsonify(users_json)


@app.route('/copy_conspect/<int:id>', methods=['POST'])
@login_required
def post_copy_conspect(id: int):
    conspect = conspect_by_id(id)
    if copy_conspect(current_user, conspect):
        return "copied"
    else:
        abort(418)
        return "error"


@app.route('/get_sample_pdf/<string:sample>', methods=['GET'])
@login_required
def get_sample_pdf(sample: str):
    print(sample)
    fragments = query_conrtoller(current_user, sample)
    pdf_name = basedir + '/static/Photo/' + pdf_fragments_by_fragments_arr(current_user, fragments)
    # print(pdf_name)
    if not os.path.exists(pdf_name):
        abort(400)
    return send_file(pdf_name, mimetype='application/pdf')



# -----------------old section-------------------
@app.route('/main/<username>', methods=['GET', 'POST'])
@login_required
def main(username=current_user, filename='Pomosch1.pdf'):
    if username != '':
        conspects = current_user.get_all_conspects()
        if request.method == 'POST':
            req = (request.form.get('img_name'))
            if req:
                print("req: " + req)
                pdf_name = pdf_fragments_by_tag(current_user, req)
                if pdf_name:
                    return render_template('build/index.html') # return render_template('osnovnaya.html', filename='Photo/'+pdf_name, conspects=conspects)
        return render_template('build/index.html') # return render_template('osnovnaya.html', filename='Photo/'+filename, conspects=conspects, currentuser=current_user.name)# return render_template('build/index.html')
    else:
        flash('please log in')
        logout()


@app.route('/openTopic/<index>', methods=['POST'])
def openTopic(index):
    conspectname = index
    # cut('0Vf2QKFahu4.jpg',0,0,200,100)
    print('creating pdf from '+conspectname)
    if check_conspect_in_base(current_user, conspectname):
        conspect = conspect_by_name(current_user, conspectname)
        pdf_name = create_pdf_conspect(user=current_user, id=conspect.id)
        if pdf_name:
            print(pdf_name)
            return main(filename=pdf_name)
        else:
            print('empty')
            return main()
    else:
        return main()


@app.route('/redactor11', methods=['GET', 'POST'])
@login_required
def redactor11():
    Rform = RedactorForm()
    if request.method == 'POST':
        if request.files.get('file'):
            conspect = request.form.get('conspect')
            photo = uploads(conspect)
            if photo is None:
                photo = default_photo
            session['redactorfoto_id'] = photo.id
            filename = photo.filename
        if Rform.submit.data:
            tags = list()
            tags.append(Rform.teg1.data)

            if Rform.teg2.data != Rform.teg3.data:
                for t in [Rform.teg2.data, Rform.teg3.data]:
                    if t:
                        if t != tags[0]:
                            tags.append(t)
            else:
                if Rform.teg2.data!=tags[0]:
                    tags.append(Rform.teg2.data)

            if (Rform.y1.data) and (Rform.x1.data) and (Rform.w.data) and (Rform.h.data):
                x1 = int(Rform.x1.data) / int(Rform.w.data)
                y1 = int(Rform.y1.data) / int(Rform.h.data)
                x2 = int(Rform.x2.data) / int(Rform.w.data)
                y2 = int(Rform.y2.data) / int(Rform.h.data)
            else:
                x1 = 0
                y1 = 0
                x2 = 1
                y2 = 1
            photo = photo_by_id(session.get('redactorfoto_id')) if session.get('redactorfoto_id') else default_photo
            fragment = add_fragment(current_user, photo, x1=x1, x2=x2, y1=y1, y2=y2)
            for t in tags:
                tag = tag_by_name(current_user, t)
                if not tag:
                    tag = add_tag(current_user, t)
                fragment.set_tag(tag)
    id = session.get('redactorfoto_id')
    filename = 'Photo/American_Beaver.jpg'
    if id:
        photo = photo_by_id(id)
        if photo:
            filename = 'Photo/users/'+photo.filename
    return render_template('redactorMisha.html', filename=filename, RF=Rform)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in Config.ALLOWED_EXTENSIONS

#---------------------------------------------------------------------

@app.route('/myconspects', methods=['GET'])
@login_required
def myconspects():
    return render_template('build/index.html')

@app.route('/myconspects/<name>/<id>/content', methods=['GET'])
@login_required
def myconspects1(name,id):
    return render_template('build/index.html')

@app.route('/myconspects/<name>/<id>/pdf', methods=['GET'])
@login_required
def myconspects2(name,id):
    return render_template('build/index.html')

@app.route('/content', methods=['GET'])
@login_required
def content():
    return render_template('build/index.html')

@app.route('/content/<name>', methods=['GET'])
@login_required
def content2(name):
    return render_template('build/index.html')


@app.route('/creteconspect/<name>/<id>', methods=['GET'])
@login_required
def creteconspect2(name,id):
    return render_template('build/index.html')

@app.route('/creteconspect/newconspect', methods=['GET'])
@login_required
def creteconspect3():
    return render_template('build/index.html')

@app.route('/redactor/<name>/<id>', methods=['GET'])
@login_required
def redactor2(name,id):
    return render_template('build/index.html')

@app.route('/comunity/', methods=['GET'])
@login_required
def comunity():
    return render_template('build/index.html')

@app.route('/comunity/<name>/<id>/conspect_and_tags', methods=['GET'])
@login_required
def comunity2(name,id):
    return render_template('build/index.html')

@app.route('/subscriberconspects/<name>/<id>/content', methods=['GET'])
@login_required
def subscriberconspects1(name,id):
    return render_template('build/index.html')

@app.route('/subscriberconspects/<name>/<id>/pdf', methods=['GET'])
@login_required
def subscriberconspects2(name,id):
    return render_template('build/index.html')




