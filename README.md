##### Зависимости проекта:
(указаны в requirements.txt)
```
Flask-Login
Flask-WTF
  ├── Flask
  │   ├── Jinja2
  │   │   └── MarkupSafe
  │   ├── Werkzeug
  │   ├── click
  │   └── itsdangerous
  └── WTForms
SQLAlchemy
```

##### Запуск:
```
.\venv\Scripts\activate.bat` (или activate.ps1 для PowerShell)
flask run
Перейти по ссылке: http://127.0.0.1:5000/

Остановить сервер: Ctrl-C
```

Для более удобного запуска проекта в PyCharm можно настроить интерпретатор и
окружение в разделе `Edit Configurations -> Python Interpreter`.
