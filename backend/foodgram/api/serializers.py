from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.serializers import UserSerializer


class IngredientSerializer(serializers.Serializer):
    "Сериализатор списка ингредиентов"
    class Meta:
        model = Ingredient
        fields = '__all__'


class TagSerializer(serializers.Serializer):
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


class RecipeGetSerializer(serializers.ModelSerializer):
    "Сериализатор получения рецепта"
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer()
    tags = TagSerializer(read_only=True)
    image = Base64ImageField()
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('id', 'ingredients', 'author', 'image',
                  'name', 'text', 'tags', 'is_favorited',
                  'is_in_shopping_cart', 'cooking_time',
                  'pub_date',)
        model = Recipe

    def get_is_favorited(self, recipe):
        request = self.context['request']
        user = request.user
        if user.is_authenticated:
            return Favorite.objects.filter(
                user=user,
                recipe=recipe
            ).exists()
        return False

    def get_is_in_shopping_cart(self, recipe):
        request = self.context['request']
        user = request.user
        if user.is_authenticated:
            return ShoppingCart.objects.filter(
                user=user,
                recipe=recipe
            ).exists()
        return False


class RecipeWriteSerializer(serializers.ModelSerializer):
    "Сериализатор создания и редактирования рецепта"
    author = UserSerializer(read_only=True)
    ingredients = IngredientSerializer()
    tags = TagSerializer(read_only=True)
    image = Base64ImageField()

    class Meta:
        fields = ('id', 'ingredients', 'author', 'image',
                  'name', 'text', 'tags', 'is_favorited',
                  'is_in_shopping_cart', 'cooking_time',)
        model = Recipe

    def create_ingredients(self, recipe, ingredients):
        for ingredient in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient_id=ingredient.get('id'),
                amount=ingredient.get('amount'), )

    def validate(self, data):
        ingredients = data['ingredients']
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError(
                    'Есть повторяющиеся ингредиенты!'
                )
            ingredients_list.append(ingredient_id)
        tags = data['tags']
        if not tags:
            raise serializers.ValidationError(
                'Нужен хотя бы один тэг для рецепта!')
        for tag_name in tags:
            if not Tag.objects.filter(name=tag_name).exists():
                raise serializers.ValidationError(
                    f'Тэга {tag_name} не существует!')
        return data

    def validate_cooking_time(self, cooking_time):
        if cooking_time < 1:
            raise serializers.ValidationError(
                'Время не может быть меньше 1 минуты')
        return cooking_time

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                'Должен быть минимум 1 ингредиент'
            )
        return ingredients

    def create(self, validated_data):
        request = self.context.get('request')
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=request.user,
            **validated_data
        )
        self.create_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, instance, validated_data):
        if 'ingredients' in validated_data:
            ingredients = validated_data.pop('ingredients')
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        if 'tags' in validated_data:
            instance.tags.set(
                validated_data.pop('tags'))
        return super().update(
            instance, validated_data)


class RecipeSmallSerializer(serializers.ModelSerializer):
    """Сериализатор получения рецептов в подписчиках."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
