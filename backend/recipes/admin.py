from django.contrib import admin

from .models import Favorite, Ingredient, Recipe, ShoppingCart, Tag


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'text', 'cooking_time', 'pub_date')
    search_fields = ('name', 'coking_time',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name', 'measurement_unit',)
    empty_value_display = '-пусто-'


class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user')
    list_filter = ('recipe', 'user')
    search_fields = ('user', )
    empty_value_display = '-пусто-'


admin.site.register(Tag)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
