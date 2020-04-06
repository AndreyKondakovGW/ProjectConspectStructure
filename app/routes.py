# Основной скрипт сайта задаёт как сайт будет отвечать на те или иные
#  запросы пользователя
from app import app
from flask import render_template, flash, redirect, url_for, session, request
from app.forms import LoginForm, RegistrationForm, RedactorForm
from app.UserDBAPI1 import user_exist, add_to_db, check_password, get_user, get_password, print_all_users
from app.config import Config, basedir
from app.DataBaseControler import check_conspect_in_base, add_conspect, conspect_by_name, get_conspect_photoes,\
        add_photo, add_photo_to_conspect, create_pdf_conspect
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app.pdf_creater import create_pdf_from_images, cut
from app.models import filename
import os


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    Lform = LoginForm()
    if Lform.submit1.data and Lform.validate():
        login(Lform)
    if current_user.is_authenticated:
        print('пользователь', current_user, 'вошёл в сеть')
        return redirect(url_for('main',username=current_user))
    return render_template('signin.html', Lform=Lform)


@app.route('/registrate', methods=['GET', 'POST'])
def registration():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    Rform = RegistrationForm()
    if Rform.submit2.data and Rform.validate():
        print('начата регистрация')
        add_to_db(name= Rform.username.data, password= Rform.password.data)
        TryLoginUser( Rform.username.data,  Rform.password.data, Rform.remember_me.data)
    return render_template('registrate.html', Rform=Rform)


@app.route('/login', methods=['GET', 'POST'])
def login(form):
    print('login')
    print(form.username.data, form.password.data)
    return TryLoginUser(form.username.data, form.password.data,form.remember_me.data)


@app.route('/logout', methods=['GET'])
def logout():
    print('пользователь', current_user, 'вышел из сети')
    logout_user()
    return redirect(url_for('index'))


@app.route('/main/<username>', methods=['GET', 'POST'])
@login_required
def main(username=current_user, filename='American_Beaver.jpg'):
    print(filename)
    if username != '':
        conspects =current_user.get_all_conspects()
        print(conspects)
        if request.method == 'POST':
            req = (request.form.get('img_name'))
            if req:
                print("req: " + req)
                if check_conspect_in_base(current_user, req):
                    pdf_name = create_pdf_conspect(current_user, req)
                    if pdf_name:
                        return render_template('osnovnaya.html', filename='Photo/'+pdf_name,conspects=conspects)
        return render_template('osnovnaya.html', filename='Photo/'+filename,conspects=conspects)
    else:
        flash('please log in')
        logout()


@app.route('/openTopic/<index>', methods=['POST'])
def openTopic(index):
    topicaname = index
    # cut('0Vf2QKFahu4.jpg',0,0,200,100)
    print('creating pdf from '+topicaname)
    dir = basedir+'/static/Topics/'+topicaname
    if os.path.exists(dir):
        files = [dir+'/'+file for file in os.listdir(dir)]
    else:
        return main()
    #for i in range(len(files)):
    #    files[i] = dir+'/' + files[i]
    pdf_name = topicaname+'_14'
    if files:
        create_pdf_from_images(pdf_name, files)
        print(pdf_name)
        return main(filename=pdf_name+'.pdf')
    else:
        print('empty')
        return main()



@app.route('/redactor', methods=['GET', 'POST'])
@login_required
def redactor():
    global filename
    Rform = RedactorForm()
    if request.method == 'POST':
        if request.files.get('file'):
            filename = uploads("conspect1", filename)
        print(filename)
        if Rform.submit.data:
            tags = Rform.teg1.data

            for t in [Rform.teg2.data, Rform.teg3.data]:
                if t:
                    tags = tags+'-'+t
            tags = basedir+'/static/Topics/'+tags
            if not(os.path.exists(tags)):
                os.mkdir(tags)
            cut(filename, int(Rform.x1.data)/int(Rform.w.data), int(Rform.y1.data)/int(Rform.h.data),\
                int(Rform.x2.data)/int(Rform.w.data), int(Rform.y2.data)/int(Rform.h.data), tags+'/'+filename)
    return render_template('redactorMisha.html', filename='Photo/'+filename, RF=Rform)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in Config.ALLOWED_EXTENSIONS


def uploads(conspect_name: str, filename: str):
    print(request)
    file = request.files.get('file')
    # print(file, allowed_file(file.filename))
    if file and allowed_file(file.filename):
            path = app.config['UPLOAD_FOLDER']+'/'+current_user.name
            if not(os.path.exists(path)):
                os.mkdir(path)
            filename1 = file.filename
            # print(filename1)
            file.save(os.path.join(path+'/', filename1))
            photo = add_photo(current_user.name+'/'+filename1)
            if (check_conspect_in_base(current_user,conspect_name)):
                conspect = conspect_by_name(current_user, conspect_name)
            else:
                conspect = add_conspect(conspect_name, current_user)
            add_photo_to_conspect(photo=photo, conspect=conspect)
            return current_user.name+'/'+filename1
    return filename


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
        '''
        user = get_user(form.username.data)
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
        '''




