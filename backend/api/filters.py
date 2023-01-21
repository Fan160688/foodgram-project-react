import django_filters as filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe
from users.models import User


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(filters.FilterSet):
    "Фильтр рецептов"
    author = filters.ModelChoiceFilter(
        queryset=User.objects.all())
    is_in_shopping_cart = filters.BooleanFilter(
        widget=filters.widgets.BooleanWidget())
    is_favorited = filters.BooleanFilter(
        widget=filters.widgets.BooleanWidget)
    tags = filters.AllValuesMultipleFilter(
        field_name='tags__slug')

    class Meta:
        model = Recipe
        fields = ['is_favorited', 'is_in_shopping_cart', 'author', 'tags']
