
ConspectBase={}
FotoBase=['photo.jpg','-AW7FLYCB-8.png','American_Beaver.jpg','0Vf2QKFahu4.jpg']


# Основные функции требующие реализацие в базе текущий код просто заглушки тагже требуется добавит больше функций для взоимодействия с базой
def check_conspect_in_base(name):
    return name in FotoBase


def add_conspet(name):
    FotoBase.append(name)
    print('пользователь загрузил фото', name, 'в базу')


def get_conspect(name):
    print('пользователь загрузил фото', name, 'из базы')
