from datetime import datetime

from django.db.models.aggregates import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST

from api.filters import RecipeFilter
from api.mixins import GetViewSet
from api.permissions import IsAuthorOrAdminOrReadOnly
from api.serializers import (IngredientSerializer, RecipeGetSerializer,
                             FavoriteSerializer, RecipeWriteSerializer,
                             TagSerializer, ShoppingCartSerializer)
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)


class IngredientsViewSet(GetViewSet):
    "Список ингредиентов"
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_fields = ['name']
    permission_classes = (AllowAny,)
    pagination_class = None


class TagsViewSet(GetViewSet):
    "Список тэгов"
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    "Представление рецептов"
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrAdminOrReadOnly, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeWriteSerializer
        return RecipeGetSerializer

    @staticmethod
    def add_method(request, pk, serializers):
        """ Метод добавления """
        data = {'user': request.user.id, 'recipe': pk}
        serializer = serializers(data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def delete_method(request, pk, model):
        obj = model.objects.filter(user=request.user, recipe__id=pk)
        if obj.exists():
            obj.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response({'errors': 'Рецепт уже удален!'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
    )
    def favorite(self, request, pk):
        """ Добавление/удаление рецептов в избранном """
        if request.method == 'POST':
            return self.add_method(
                request=request,
                pk=pk,
                serializers=FavoriteSerializer)
        return self.delete_method(
                request=request,
                pk=pk,
                model=Favorite)

    @action(
        detail=True,
        methods=['post', 'delete'],
    )
    def shopping_cart(self, request, pk):
        """ Добавление/удаление рецептов в списке покупок """
        if request.method == 'POST':
            return self.add_method(
                request,
                pk,
                serializers=ShoppingCartSerializer)
        return self.delete_method(
                request,
                pk,
                model=ShoppingCart)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        """ Скачивание файла со списком покупок """
        user = request.user
        if not user.shopping_cart.exists():
            return Response(status=HTTP_400_BAD_REQUEST)

        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        today = datetime.today()
        shopping_cart = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {today:%Y-%m-%d}\n\n'
        )
        shopping_cart += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measure"]})'
            f' - {ingredient["ingredient_value"]}'
            for ingredient in ingredients
        ])
        shopping_cart += f'\n\nFoodgram ({today:%Y})'

        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_cart, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
