import csv

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загрузка данных из csv файлов'

    def handle(self, *args, **kwargs):

        try:
            with open(
                f'{settings.BASE_DIR}/foodgram/static/data/ingredients.csv', 'r', encoding='utf-8'
            ) as file:
                reader = csv.DictReader(file)
                Ingredient.objects.bulk_create(
                    Ingredient(**data) for data in reader
                )
            self.stdout.write(self.style.SUCCESS('Ингредиенты загружен'))
        except FileNotFoundError:
            raise CommandError('Добавьте файл ingredients в директорию data')
