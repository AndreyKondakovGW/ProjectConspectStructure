from flask_login import UserMixin
#from app import login,db;
import random

ROLE_USER = 0
ROLE_ADMIN = 1
ID_VALUE = 1010


def gererate_id():
    return ID_VALUE+random.randint(1,100)


# Демо версия класс пользователья которую потом надо будет реализовать через базу данных
class User(UserMixin):
    def __init__(self, nickname,password):
        self.id = gererate_id()
        self.nickname = nickname
        self.password=int(password)

 #   @login.user_loader
  #  def load_user(user_id):
   #     return db[user_id]

    def __repr__(self):
        return '<User %r>' % (self.nickname)
