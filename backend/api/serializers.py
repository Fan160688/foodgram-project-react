from django.db.transaction import atomic
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from users.serializers import CustomUserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    "Сериализатор списка ингредиентов"
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class TagSerializer(serializers.ModelSerializer):
    "Сериализатор тегов"
    class Meta:
        model = Tag
        fields = (
            'id', 'name', 'color', 'slug',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = (
            'id', 'name', 'measurement_unit', 'amount')


class AddIngredientRecipeSerializer(serializers.ModelSerializer):
    """ Сериализатор добавление ингридиентов в рецепт """
    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    "Сериализатор получения рецепта"
    author = CustomUserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField()
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited')
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ('id', 'ingredients', 'author', 'image',
                  'name', 'text', 'tags', 'is_favorited',
                  'is_in_shopping_cart', 'cooking_time')
    
    def get_ingredients(self, obj):
        ingredients = RecipeIngredient.objects.filter(recipe=obj)
        return RecipeIngredientSerializer(ingredients, many=True).data

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request.user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=request.user, recipe__id=obj.id).exists()

    def get_is_in_shopping_cart(self, obj):
        if request.user.is_anonymous:
            return False
        request = self.context.get('request')
        return ShoppingCart.objects.filter(
            user=request.user, recipe__id=obj.id).exists()


class RecipeWriteSerializer(serializers.ModelSerializer):
    "Сериализатор создания и редактирования рецепта"
    author = CustomUserSerializer(read_only=True)
    ingredients = AddIngredientRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True,
    )
    image = Base64ImageField(use_url=True, max_length=None)

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'tags',
                  'image', 'name', 'text', 'cooking_time')
    
    def create_ingredients(self, ingredients, recipe):
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                ingredient=Ingredient.objects.get(id=ingredient['id']),
                recipe=recipe,
                amount=ingredient['amount'],
            ) for ingredient in ingredients]
        )

    # def validate(self, data):
    #     ingredients = self.initial_data.get('ingredients')
    #     ingredients_list = []
    #     for ingredient in ingredients:
    #         ingredient_id = ingredient['id']
    #         if ingredient_id in ingredients_list:
    #             raise serializers.ValidationError(
    #                 'Есть повторяющиеся ингредиенты!'
    #             )
    #         ingredients_list.append(ingredient_id)
    #     if data['cooking_time'] <= 0:
    #         raise serializers.ValidationError(
    #             'Время приготовления должно быть больше 0!'
    #         )
    #     return data
    
    @atomic
    def create(self, validated_data):
        """ Создание рецепта """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(
            author=author, **validated_data
        )
        self.create_ingredients(recipe=recipe, ingredients=ingredients)
        recipe.tags.set(tags)
        return recipe

    @atomic
    def update(self, instance, validated_data):
        """ Изменение рецепта """
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        instance = super().update(instance, validated_data)
        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self.create_ingredients(recipe=instance,
                                ingredients=ingredients
                                )
        instance.save()
        return instance

    def to_representation(self, instance):
        return RecipeGetSerializer(instance, context={
            'request': self.context.get('request')
        }).data


class RecipeSmallSerializer(serializers.ModelSerializer):
    """Сериализатор получения рецептов в подписчиках."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    """ Сериализатор списка покупок """
    class Meta:
        model = ShoppingCart
        fields = ('recipe', 'user')

    def validate(self, data):
        request = self.context.get('request')
        recipe = data['recipe']
        if ShoppingCart.objects.filter(
            user=request.user, recipe=recipe
        ).exists():
            raise ValidationError({
                'errors': 'Рецепт уже есть в корзине.'
            })
        return data

    def to_representation(self, instance):
        return RecipeSmallSerializer(instance.recipe, context={
            'request': self.context.get('request')
        }).data
