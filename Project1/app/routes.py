from app import app
from flask import render_template, flash, redirect, url_for, g,request
from app.forms import LoginForm
from flask_login import current_user, login_user
from app import db,UserDBAPI
from app.models import User
from app.config import Config
import os


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in Config.ALLOWED_EXTENSIONS


@app.route('/uploads',methods=['GET', 'POST'])
def uploads():
    print(request)
    if request.method == 'POST':
        file = request.files['file']
    if file and allowed_file(file.filename):
            filename = file.filename
            print(filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
    return redirect(url_for('index'))


@app.route('/redactor')
def redactor():
    return render_template('redactorMisha.html')


@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template('home.html')


@app.route('/registrate', methods=['GET', 'POST'])
def Registration():
    form = LoginForm()
    if form.validate_on_submit():
        UserDBAPI.add_to_db(form.username.data, User(form.username.data,form.password.data))
        #flash('User Added'+form.username.data+'/'+form.password.data)
        current_user=form.username.data
        return redirect(url_for('main',username=current_user))
    return render_template('RegestrationMishaF.html', title='Regestration', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        if not (UserDBAPI.right_user_data(form.username.data,form.password.data)):
            flash('Wrong login or password')
            UserDBAPI.show_all_user()
            return redirect(url_for('index'))
        current_user=form.username.data
        return redirect(url_for('main',username=current_user))
    return render_template('LoginMishaF.html', title='Sign In', form=form)


@app.route('/main/<username>', methods=['GET', 'POST'])
def main(username):
    return render_template('osnovnaya.html',user=username)

