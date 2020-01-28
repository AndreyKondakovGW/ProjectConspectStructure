# Основной скрипт сайта задаёт как сайт будет отвечать на те или иные запросы пользователя
from app import app
from flask import render_template, flash, redirect, url_for, session, request
from app.forms import LoginForm
from app import UserDBAPI
from app.models import User,db,UserDB,get_user
from app.config import Config
from app.DataBaseControler import check_conspect_in_base,add_conspet,get_conspect
import os


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    if ('user' in session):
        print('пользователь', session['user'], 'вошёл в сеть')
        return redirect(url_for('main',username=session['user']))
    return render_template('home.html')


@app.route('/registrate', methods=['GET', 'POST'])
def Registration():
    form = LoginForm()
    if form.validate_on_submit():
        if not(user_exist(form.username.data)):
            add_user(form.username.data,form.password.data)
            return TryLoginUser(form.username.data,form.password.data)
        else:
            print('пользователь существует')
            return redirect(url_for('Registration'))
    return render_template('RegestrationMishaF.html', title='Regestration', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
     form = LoginForm()
     if form.validate_on_submit():
        return TryLoginUser(form.username.data,form.password.data)
     return render_template('LoginMishaF.html', title='Sign In', form=form)

@app.route('/logout', methods=['GET'])
def logout():
    print('пользователь', session['user'], 'вышел из сети')
    session.pop('user')
    return redirect(url_for('index'))


@app.route('/main/<username>', methods=['GET', 'POST'])
def main(username='', filename='American_Beaver.jpg'):
    if (username!=''):
        if request.method == 'POST':
             req =(request.form.get('img_name'))
             if (check_conspect_in_base(req)):
                get_conspect(req)
                return render_template('osnovnaya.html',filename=req)
        return render_template('osnovnaya.html',filename=filename)
    else:
        flash('please log in')
        logout()


@app.route('/redactor', methods=['GET', 'POST'])
def redactor():
    if (request.method == 'POST'):
        print(request.files['upload'])
        # add_file
    return render_template('redactorMisha.html')


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
            file.save(os.path.join(app.config['Photo'],filename))
    return redirect(url_for('index'))


def TryLoginUser(name,password):
     if (db[name].password==int(password)):
         session['user']=name
         return redirect(url_for('index'))
     else:
         return redirect(url_for('login'))
        # user = get_user(form.username.data)
      #  if user is None or not user.check_password(form.password.data):
      #      flash('Invalid username or password')
       #     return redirect(url_for('login'))
      #  login_user(user, remember=form.remember_me.data)
     #   return redirect(url_for('index'))

def user_exist(name):
    return db.get(name)

def add_user(name,password):
    UserDBAPI.add_to_db(name,password)
