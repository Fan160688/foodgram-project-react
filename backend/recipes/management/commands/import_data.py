import csv

from django.conf import settings
from django.core.management import BaseCommand, CommandError

from recipes.models import Ingredient


class Command(BaseCommand):
    help = 'Загружаем csv-файл'

    def handle(self, *args, **kwargs):
        data_path = settings.BASE_DIR
        try:
            with open(
                f'{data_path}/data/ingredients.csv', 'r', encoding='utf-8'
            ) as file:
                reader = csv.DictReader(file)
                Ingredient.objects.bulk_create(
                    Ingredient(**data) for data in reader
                )
            self.stdout.write(self.style.SUCCESS('Ингредиенты загружен'))
        except FileNotFoundError:
            raise CommandError('Добавьте файл ingredients в директорию data')
