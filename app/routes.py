# Основной скрипт сайта задаёт как сайт будет отвечать на те или иные
#  запросы пользователя
from app import app
from flask import render_template, flash, redirect, url_for, session, request, jsonify, send_file, abort
from app.forms import LoginForm, RegistrationForm, RedactorForm
from app.UserDBAPI1 import user_exist, add_to_db, check_password, get_user, get_password, print_all_users, check_access
from app.config import Config, basedir
from app.DataBaseControler import check_conspect_in_base, add_conspect, conspect_by_name, get_conspect_photoes,\
        add_photo, add_photo_to_conspect, create_pdf_conspect, tag_by_name, add_tag, add_fragment, pdf_fragments_by_tag,\
        photo_by_id, tag_by_id, conspect_by_id, delete_conspect_by_id, delete_photo_db, all_photo_fragments, remove_from_conspect
from flask_login import current_user, login_user, logout_user, login_required
from app import login_manager
from werkzeug.urls import url_parse
from app.pdf_creater import create_pdf_from_images, cut
from app.models import filename, default_photo, AccessDB
from tempfile import NamedTemporaryFile
import os


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    Lform = LoginForm()
    if Lform.submit1.data and Lform.validate():
        login(Lform)
    if current_user.is_authenticated:
        print('пользователь', current_user, 'вошёл в сеть')
        return redirect(url_for('main', username=current_user))
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


# выдаёт список конспектов пользователя в виде JSON-массива
@app.route('/getconspects', methods=['GET'])
@login_required
def get_conspects():
    """return all user's conspects in JSON - list of dicts with 'id' and 'name' keys"""
    user = current_user
    conspects = user.get_all_conspects()
    jsonlist = list()
    for conspect in conspects:
        jsonlist.append({"id": conspect.id, "name": conspect.name})
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
    print(pdf_name)
    print(os.path.exists(pdf_name))
    return send_file(pdf_name, mimetype='application/pdf')


@app.route('/getconspectphotos/<int:id>', methods=['GET'])
@login_required
def get_conspect_photos(id: int):
    """return all photoes in conspects (only information about photoes, not files themself"""
    print(id)
    print(type(id))
    user = current_user
    conspect = conspect_by_id(id)
    if not conspect:
        abort(404)
    if not check_access(user, conspect):
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
    if not check_access(current_user, conspect):
        abort(403)
    return send_file('static/Photo/users/'+photo.filename, mimetype='image')


@app.route('/getconspectpdf/<string:conspectname>')
@login_required
def get_conspect_pdf(conspectname: str):
    pdf_name = create_pdf_conspect(current_user, conspectname)
    if pdf_name:
        pdf_name = "static/Photo/"+pdf_name
    else:
        abort(404)
    return send_file(pdf_name, mimetype='application/pdf')


@app.route('/savephoto/<string:conspectname>', methods=['POST'])
@login_required
def save_conspect_photo(conspectname: str):
    # session['redactorfoto_id'] = default_photo
    photo = uploads(conspectname)
    if photo is None:
        abort(400)
        photo = default_photo
    # session['redactorfoto_id'] = photo.id
    return jsonify({"id": photo.id, "filename": photo.filename, "id_conspect": photo.id_conspect})


def uploads(conspect_name: str):
    file = request.files.get('file')
    if file and allowed_file(file.filename):
            path = app.config['UPLOAD_FOLDER']+'/users/'+current_user.name
            if not(os.path.exists(path)):
                os.mkdir(path)
            #filename1 = file.filename
            #file.save(os.path.join(path+'/', filename1))
            filename1 = filename_gen(path, file)
            photo = add_photo(current_user.name+'/'+filename1)
            if check_conspect_in_base(current_user, conspect_name):
                conspect = conspect_by_name(current_user, conspect_name)
            else:
                conspect = add_conspect(conspect_name, current_user)
            add_photo_to_conspect(photo=photo, conspect=conspect)
            return photo
    return None


@app.route('/deletephoto/<int:id>', methods=['DELETE'])
@login_required
def delete_photo(id: int):
    print(id)
    photo = photo_by_id(id)
    conspect = conspect_by_id(photo.id_conspect)
    if check_access(current_user, conspect):
        fragments = all_photo_fragments(photo)
        if fragments:
            remove_from_conspect(photo)
        else:
            delete_photo_db(photo)


@app.route('/deleteconspect/<int:id>', methods=['DELETE'])
def delete_conspect(id: int):
    ...


@app.route("/sendfragment", methods=['POST'])
@login_required
def post_fragment():
    user = current_user
    # user = get_user(username)
    data = request.get_json()
    # data == {"photo_id": id, "x1": x1, "y1": y1, "x2": x2, "y2": y2, "tags": [tag1, tag2]}
    photo_id = data.get("photo_id")
    if photo_id:
        photo = photo_by_id(photo_id)
    else:
        photo = default_photo
    x1 = data.get("x1")
    y1 = data.get("y1")
    x2 = data.get("x2")
    y2 = data.get("y2")
    if not (x1 and x2 and y1 and y2):
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


# -----------------old section-------------------

@app.route('/main/<username>', methods=['GET', 'POST'])
@login_required
def main(username=current_user, filename='Pomosch1.pdf'):
    print(filename)
    if username != '':
        conspects =current_user.get_all_conspects()
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
        pdf_name = create_pdf_conspect(user=current_user, conspect_name=conspectname)
        if pdf_name:
            print(pdf_name)
            return main(filename=pdf_name)
        else:
            print('empty')
            return main()
    else:
        return main()


@app.route('/redactor', methods=['GET', 'POST'])
@login_required
def redactor():
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


def filename_gen(path: str, file):
    ext = file.filename.split('.')[1]
    tf = NamedTemporaryFile(dir=path)
    filename = tf.name+'.'+ext
    tf.close()
    while os.path.exists(filename):
        tf = NamedTemporaryFile(dir=path)
        filename = tf.name + '.' + ext
        tf.close()
    file.save(filename)
    filename = filename.split('/')[-1]
    return filename










