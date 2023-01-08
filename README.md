# praktikum_new_diplom
# Установка

## 1) Склонировать репозиторий
## 2) Создать и активировать виртуальное окружение для проекта

python -m venv venv

source venv/scripts/activate

## 3) Установить зависимости
python pip install -r requirements.txt

## 4) Сделать миграции
python manage.py makemigrations
python manage.py migrate

## 5) Запустить сервер
python manage.py runserver