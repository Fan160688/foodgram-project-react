from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    IngredientInRecipe,
    Recipe,
    ShoppingList,
    Tag
)

admin.site.empty_value_display = 'Значение отсутствует'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """Класс настройки раздела тегов"""

    list_display = ('pk', 'name', 'slug')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Класс настройки раздела игредиентов"""

    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)


class TabularRecipeIngredientAdmin(admin.TabularInline):
    model = IngredientInRecipe
    fk_name = 'recipe_parent'
    extra = 1


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorited')
    list_filter = ('author', 'name', 'tags')
    exclude = ('ingredients',)
    search_fields = ('^name',)
    filter_horizontal = ('tags',)
    inlines = [
        TabularRecipeIngredientAdmin,
    ]

    def favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    favorited.short_description = 'Кол-во людей добавивших в избранное'


@admin.register(IngredientInRecipe)
class IngredientRecipeAdmin(admin.ModelAdmin):
    """Класс настройки соответствия ингредиентов и рецепта"""

    list_display = ('pk', 'ingredient', 'amount')


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user__username', 'user__email')
    empty_value_display = '-пусто-'
