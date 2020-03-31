# Основной скрипт сайта задаёт как сайт будет отвечать на те или иные
#  запросы пользователя
from app import app
from flask import render_template, flash, redirect, url_for, session, request
from app.forms import LoginForm, RegistrationForm
from app.UserDBAPI1 import user_exist, add_to_db, check_password, get_user, get_password, print_all_users
from app.config import Config
from app.DataBaseControler import check_conspect_in_base, add_conspect, \
     get_conspect
import os


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    #print(db)
    print_all_users()
    Lform = LoginForm()
    Rform = RegistrationForm()
    if Lform.submit1.data and Lform.validate():
        login(Lform)
    if Rform.submit2.data and Rform.validate():
        registration(Rform)
    if ('user' in session):
        print('пользователь', session['user'], 'вошёл в сеть')
        return redirect(url_for('main', username=session['user']))
    return render_template('signin.html', Lform=Lform, Rform=Rform)


@app.route('/registrate', methods=['GET', 'POST'])
def registration(form):
    print('registration')
    if not(user_exist(form.username.data)):
        print('начата регистрация')
        add_to_db(name=form.username.data, password=form.password.data)
        return TryLoginUser(form.username.data, form.password.data)
    else:
        print('пользователь существует')
        return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login(form):
    print('login')
    print(form.username.data, form.password.data)
    return TryLoginUser(form.username.data, form.password.data)


@app.route('/logout', methods=['GET'])
def logout():
    print('пользователь', session['user'], 'вышел из сети')
    session.pop('user')
    return redirect(url_for('index'))


@app.route('/main/<username>', methods=['GET', 'POST'])
def main(username='', filename='American_Beaver.jpg'):
    if (username != ''):
        if request.method == 'POST':
            req = (request.form.get('img_name'))
            if (check_conspect_in_base(req)):
                get_conspect(req)
                return render_template('osnovnaya.html', filename='Photo/'+req)
        return render_template('osnovnaya.html', filename='Photo/'+filename)
    else:
        flash('please log in')
        logout()


@app.route('/redactor', methods=['GET', 'POST'])
def redactor(filename='American_Beaver.jpg'):
    username = session['user']
    # if (request.method == 'POST'):
    #   print(request.files['upload'])
    # add_file
    return render_template('redactorMisha.html', filename='Photo/'+filename)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in Config.ALLOWED_EXTENSIONS


def uploads():
    print(request)
    if request.method == 'POST':
        file = request.files['upload']
    if file and allowed_file(file.filename):
            filename = file.filename
            print(filename)
            file.save(os.path.join(app.config['Photo'], filename))
    return redirect(url_for('index'))


def TryLoginUser(name, password):
    if user_exist(name):
        print('пользователь существует')
        if check_password(name, password):
            session['user'] = name
            return redirect(url_for('index'))
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




