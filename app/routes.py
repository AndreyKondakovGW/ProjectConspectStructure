# Основной скрипт сайта задаёт как сайт будет отвечать на те или иные
#  запросы пользователя
from app import app
from flask import render_template, flash, redirect, url_for, session, request
from app.forms import LoginForm, RegistrationForm, RedactorForm
from app.UserDBAPI1 import user_exist, add_to_db, check_password, get_user, get_password, print_all_users
from app.config import Config, basedir
from app.DataBaseControler import check_conspect_in_base, add_conspect, conspect_by_name, get_conspect_photoes,\
        add_photo, add_photo_to_conspect, create_pdf_conspect, tag_by_name, add_tag, add_fragment, pdf_fragments_by_tag,\
        photo_by_id
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.pdf_creater import create_pdf_from_images, cut
from app.models import filename, default_photo
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
def logout():
    print('пользователь', current_user, 'вышел из сети')
    logout_user()
    session.clear()
    return redirect(url_for('index'))


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
                    return render_template('osnovnaya.html', filename='Photo/'+pdf_name, conspects=conspects)
        return render_template('osnovnaya.html', filename='Photo/'+filename, conspects=conspects, currentuser=current_user.name)
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
            photo = uploads(conspect, default_photo)
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

                # cut(filename, int(Rform.x1.data)/int(Rform.w.data), int(Rform.y1.data)/int(Rform.h.data),
                #   int(Rform.x2.data)/int(Rform.w.data), int(Rform.y2.data)/int(Rform.h.data), tags+'/'+filename)
    id = session.get('redactorfoto_id')
    filename = 'Photo/American_Beaver.jpg'
    if id:
        photo = photo_by_id(id)
        if photo:
            filename = 'Photo/'+photo.filename
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


def uploads(conspect_name: str, default_photo):
    file = request.files.get('file')
    if file and allowed_file(file.filename):
            path = app.config['UPLOAD_FOLDER']+'/'+current_user.name
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
    return default_photo


def TryLoginUser(name, password,remember_me):
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




