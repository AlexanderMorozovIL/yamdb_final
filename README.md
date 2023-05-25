# API для проекта YaMDB в контейнере Docker
[![API for YaMDB project workflow](https://github.com/bondarval/yamdb_final/actions/workflows/yamdb_workflow.yml/badge.svg?branch=main)](https://github.com/AlexanderMorozovIL/yamdb_final/blob/master/.github/workflows/yamdb_workflow.yml)

### Краткое описание проекта:

Проект YaMDb собирает отзывы пользователей на произведения. Сами произведения в YaMDb не хранятся, здесь нельзя посмотреть фильм или послушать музыку.

Данный проект позволяет ставить произведениям оценку и комментировать чужие отзывы.

Произведения делятся на категории, и на жанры. Список произведений, категорий и жанров может быть расширен администратором.

Полный список запросов и эндпоинтов описан в документации ReDoc, доступна после запуска проекта по адресу:
```
http://127.0.0.1:8000/redoc/
```

### Как запустить проект:
Клонировать репозиторий, перейти в директорию с проектом.

```
git clone https://github.com/AlexanderMorozovIL/api_yamdb.git
```

Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```

```
source venv/Scripts/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Выполнить миграции:

```
python manage.py makemigrations
```
```
python manage.py migrate
```

Запустить проект:

```
python manage.py runserver
```

### Авторизация пользователей:
Для получения доступа необходимо создать пользователя отправив POST запрос на эндпоинт ```/api/v1/auth/signup/``` username и email.

Запрос:
```
{
"email": "string",
"username": "string"
}
```
Далее на email придет код подтверждения, который вместе с username необходимо отправить POST запросом на эндпоинт```/api/v1/auth/token/```

Запрос:
```
{
"username": "string",
"confirmation_code": "string"
}
```
Ответ:
```
{
"access": "string"
}
```
Данный токен используется для дальнейшей авторизации.

Для просмотра и изменения своих данных используйте эндпоинт ```/api/v1/users/me/```

### Примеры запросов к API:

Получение списка всех категорий:

```
http://127.0.0.1:8000/api/v1/categories/
```
Получение списка всех жанров:

```
http://127.0.0.1:8000/api/v1/genres/
```

Получение списка всех произведений:

```
http://127.0.0.1:8000/api/v1/titles/
```


Авторы:
```
https://github.com/AlexanderMorozovIL - Александр Морозов (teamlead)
```
```
https://github.com/OMakhony - Махонская Ольга
```
```
https://github.com/SafonovaEkaterina - Сафонова Екатерина
```
