# Проект Foodgram «Продуктовый помощник»

![Build Status](https://github.com/fan160688/foodgram-project-react/actions/workflows/yamdb_workflow.yml/badge.svg)

## Описание проекта

 На этом сервисе пользователи могут публиковать рецепты, подписываться на публикации других пользователей, добавлять понравившиеся рецепты в список «Избранное», а перед походом в магазин скачивать сводный список продуктов, необходимых для приготовления одного или нескольких выбранных блюд.


## Локальная установка проекта

Клонировать репозиторий и перейти в него в командной строке:
git clone https:
foodgram-project-react
Cоздать и активировать виртуальное окружение:

```
python -m venv venv
```
```
source venv/scripts/activate
```
Или на Linux
```
source venv/bin/activate
```

Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

Создать и заполнить файл .env с переменными окружения для settings.py:

```
cd infra
```

```
touch .env
```

Создать и запустить контейнеры с проектом:

```
docker-compose up -d --build
```

Выполнить миграции модели users:

```
docker-compose exec web python manage.py makemigrations users
```

Выполнить миграции:

```
docker-compose exec backend python manage.py migrate
```

Создать суперпользователя:

```
docker-compose exec backend python manage.py createsuperuser
```

Собрать статику:

```
docker-compose exec backend python manage.py collectstatic --no-input
```

Добавить данные в базу:

```
docker-compose exec backend python add_data.py
```