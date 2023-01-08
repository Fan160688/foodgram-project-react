import io
from django.shortcuts import render
from api.filters import RecipeFilter
from api.serializers import (IngredientSerializer, TagSerializer,
                             RecipeIngredientSerializer, RecipeGetSerializer,
                             RecipeWriteSerializer, RecipeSmollSerializer)
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from datetime import datetime
from django.db.models import Avg
from rest_framework.status import HTTP_400_BAD_REQUEST
from django.db.models.aggregates import Count, Sum
from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets, mixins, permissions
from rest_framework.decorators import action, api_view
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from recipes.models import Ingredient, Tag, Recipe, RecipeIngredient, Favorite, ShoppingCart
from users.models import User
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from django.http import HttpResponse

from api.permissions import (AdminModeratorAuthorPermission, IsAdmin,
                             IsAdminUserOrReadOnly)


class IngredientsViewSet(mixins.ListModelMixin,
                         mixins.RetrieveModelMixin,
                         viewsets.GenericViewSet):
    "Список ингредиентов"
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (filters.SearchFilter,)
    filterset_class = ('name',)
    permission_classes = (IsAdminUserOrReadOnly,)
    pagination_class = None


class TagsViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    "Список тэгов"
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdminUserOrReadOnly,)
    pagination_class = None


class RecipesViewSet(viewsets.ModelViewSet):
    "Представление рецептов"
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.action == 'create' or self.action == 'partial_update':
            return RecipeWriteSerializer
        return RecipeGetSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk):
        """ Добавление/удаление рецептов в избранном """
        if request.method == 'POST':
            if Favorite.objects.filter(
                    user=request.user,
                    recipe__id=pk).exists():
                return Response({'errors': 'Рецепт уже добавлен!'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipe, id=pk)
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeSmollSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            obj = Favorite.objects.filter(user=request.user, recipe__id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепт уже удален!'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk):
        """ Добавление/удаление рецептов в списке покупок """
        if request.method == 'POST':
            if ShoppingCart.objects.filter(
                    user=request.user,
                    recipe__id=pk).exists():
                return Response({'errors': 'Рецепт уже добавлен!'},
                                status=status.HTTP_400_BAD_REQUEST)
            recipe = get_object_or_404(Recipe, id=pk)
            Favorite.objects.create(user=request.user, recipe=recipe)
            serializer = RecipeSmollSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            obj = ShoppingCart.objects.filter(user=request.user, recipe__id=pk)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response({'errors': 'Рецепт уже удален!'},
                            status=status.HTTP_400_BAD_REQUEST)

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
        shopping_list = (
            f'Список покупок для: {user.get_full_name()}\n\n'
            f'Дата: {today:%Y-%m-%d}\n\n'
        )
        shopping_list += '\n'.join([
            f'- {ingredient["ingredient__name"]} '
            f'({ingredient["ingredient__measure"]})'
            f' - {ingredient["amount"]}'
            for ingredient in ingredients
        ])
        shopping_list += f'\n\nFoodgram ({today:%Y})'

        filename = f'{user.username}_shopping_list.txt'
        response = HttpResponse(shopping_list, content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
