from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомни меня')
    submit = SubmitField('Вход')


class RegistrationForm(FlaskForm):
    username = StringField('Придумайте Логин', validators=[DataRequired()])
    password = PasswordField('Придумайте Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомни меня')
    submit = SubmitField('Зарегистрироваться')
