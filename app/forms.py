from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.UserDBAPI1 import user_exist, check_password


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомни меня')
    submit1 = SubmitField('Вход')

    def validate_username(self, username):
        if not(user_exist(username.data)):
            raise ValidationError('This user not exist.')

    def validate_password(self, password):
        print(password.data,self.username.data)

        if not(check_password(self.username.data,password.data)):
            raise ValidationError('Wrong password.')


class RegistrationForm(FlaskForm):
    username = StringField('Придумайте Логин', [Length(min=4, max=25,message="Username to short or too long")])
    password = PasswordField('Придумайте Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомни меня')
    submit2 = SubmitField('Зарегистрироваться')

    def validate_username(self, username):
        if user_exist(username.data):
            raise ValidationError('Please use a different username.')

class RedactorForm(FlaskForm):
    teg1=StringField('Добавте тег', validators=[DataRequired()])
    teg2=StringField('Добавте тег')
    teg3=StringField('Добавте тег')
    comments=StringField('Добавте комментарий')
    w=StringField()
    h=StringField()
    x1=StringField()
    x2=StringField()
    y1=StringField()
    y2=StringField()
    submit = SubmitField('сохранить')
