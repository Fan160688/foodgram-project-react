from colorfield.fields import ColorField
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from users.validators import name_validator

User = get_user_model()


class Tag(models.Model):
    """Класс тегов"""

    name = models.CharField(
        verbose_name='Тег',
        max_length=settings.NAME_MAX_LENGTH,
        unique=True,
        validators=[name_validator]
    )
    color = ColorField(
        verbose_name='Hex-цвет',
        format='hex',
        max_length=7,
        unique=True
    )
    slug = models.SlugField(
        verbose_name='slug',
        max_length=settings.SLUG_MAX_LENGTH,
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self) -> str:
        return f'{self.name}, {self.slug}, цвет: {self.color}'


class Ingredient(models.Model):
    """Класс ингредиентов"""

    name = models.CharField(
        max_length=settings.NAME_MAX_LENGTH,
        verbose_name='Название',
        validators=[name_validator],
        unique=True,
        blank=False
    )
    measurement_unit = models.CharField(
        max_length=20,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('id',)

    def __str__(self):
        return self.name


class IngredientInRecipe(models.Model):
    """ Модель ингредиентов в рецепте. """
    recipe_parent = models.ForeignKey(
        'Recipe',
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='+'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Название ингредиента в рецепте',
        related_name='+',
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество ингредиента в рецепте',
        default='г',
        validators=[
            MinValueValidator(
                1,
                message='Количество ингредиентов не может быть меньше 1.'
            ),
        ]
    )

    class Meta:
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = 'Количество ингредиентов в рецептах'
        constraints = [
            models.UniqueConstraint(
                fields=['ingredient', 'recipe_parent'],
                name='recipe_ingredient_unique',
            )
        ]

    def __str__(self) -> str:
        return (
            f"{self.ingredient} в рецепте {self.recipe_parent} - "
            f"{self.amount} {self.ingredient.measurement_unit}"
        )


class Recipe(models.Model):
    """ Модель рецептов. """
    name = models.CharField(
        verbose_name='Название рецепта',
        validators=[name_validator],
        max_length=200,
        unique=True,
        error_messages={
            'unique': "Рецепт с таким названием уже создан."
        },
    )
    image = models.ImageField(
        verbose_name='Фото',
        upload_to='recipes/images'
    )
    text = models.TextField(
        verbose_name='Описание рецепта'
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Тэги',
        symmetrical=False,
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта',
        related_name="recipes"
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации',
        auto_now_add=True
    )
    ingredients = models.ManyToManyField(
        IngredientInRecipe,
        related_name='recipe',
        null=False,
        blank=True
    )
    cooking_time = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(
                1,
                message='Время приготовления не может быть меньше 1 мин.'
            ),
        ],
        verbose_name='Время приготовления, мин.',
        help_text=(
            "Не может быть меньше минуты!"
        ),
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class Favorite(models.Model):
    """Класс избранное"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
        related_name='favorites',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='favoriting',
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingList(models.Model):
    """Вспомогательный класс для формирования списка покупок"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shop_list',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='shop_list',
    )

    class Meta:
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Список покупок'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shoppingList'
            ),
        ]

    def __str__(self):
        return f'{self.user} {self.recipe}'
