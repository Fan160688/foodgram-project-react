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
        return Recipe.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.image = validated_data.get('image', instance.image)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time',
            instance.cooking_time
        )
        instance.save()
        return instance


class RecipeSmollSerializer(serializers.ModelSerializer):
    """Сериализатор получения рецептов в подписчиках."""
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
        read_only_fields = ('id', 'name', 'image', 'cooking_time')
