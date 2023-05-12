# Стек
<img src="https://img.shields.io/badge/Python-4169E1?style=for-the-badge"/> <img src="https://img.shields.io/badge/Django-008000?style=for-the-badge"/>

# Описание
### Проект Yatube

Проект представляет из себя блог, в котором пользователи могут размещать посты, оставлять комментарии, подписываться на авторов.

### Как запустить проект:

*Клонировать репозиторий и перейти в него в командной строке:*
```
https://github.com/qzonic/hw05_final.git
```
```
cd hw05_final/
```

*Cоздать и активировать виртуальное окружение:*
```
python -m venv venv
```
* Windows
```
venv\Scripts\activate.bat
```
* Linux/MacOS.
```
source venv/bin/activate
```

*Установить зависимости из файла requirements.txt:*
```
pip install --upgrade pip
```

```
pip install -r requirements.txt
```

*Перейдите в директорию с файлом manage.py и выполните миграции:*
```
cd yatube/
```

```
python manage.py makemigrations
```
```
python manage.py migrate
```

*Создать супер пользователя*
```
python manage.py createsuperuser
```

*Запустить проект:*
```
python manage.py runserver
```

### Автор
[![telegram](https://img.shields.io/badge/Telegram-Join-blue)](https://t.me/qzonic)
