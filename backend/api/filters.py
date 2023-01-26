from django_filters.rest_framework import FilterSet, filters
from rest_framework.filters import SearchFilter

from recipes.models import Recipe, Tag


class IngredientSearchFilter(SearchFilter):
    search_param = 'name'


class RecipeFilter(FilterSet):
    """ Фильтр для рецептов и тегов. """

    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.CharFilter(
        field_name='is_favorited', method='get_is_favorited'
    )
    is_in_shopping_cart = filters.CharFilter(
        field_name='is_in_shopping_cart', method='get_is_in_shopping_cart'
    )
    author = filters.AllValuesMultipleFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def get_is_favorited(self, queryset, name, data):
        if data and not self.request.user.is_anonymous:
            return queryset.filter(favoriting__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, data):
        if data and not self.request.user.is_anonymous:
            return queryset.filter(
                shop_list__user=self.request.user
            )
        return queryset
