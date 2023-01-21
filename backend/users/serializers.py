from djoser.serializers import UserCreateSerializer, UserSerializer

from rest_framework import serializers

from recipes.models import Recipe

from .models import Subscribe, User


class SubscribeRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CustomUserCreateSerializer(UserCreateSerializer):
    """ Сериализатор создания пользователя. """
    class Meta:
        model = User
        fields = ('email', 'username', 'first_name',
                  'last_name', 'password'
                  )


class CustomUserSerializer(UserSerializer):
    "Сериализатор просмотра пользователей"
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=request.user, author=obj).exists()


class SubscribeSerializer(serializers.ModelSerializer):
    """Сериализатор просмотра подписок."""
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.BooleanField(
        read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        read_only=True)

    class Meta:
        model = Subscribe
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed', 'recipes', 'recipes_count',)

    def get_is_subscribed(self, subscr):
        user = self.context('request').user
        if user.is_authenticated:
            return Subscribe.objects.filter(author=subscr.author,
                                            user=user).exists()
        return False

    def get_recipes(self, subscr):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = (
            subscr.author.recipe.all()[:int(limit)] if limit
            else subscr.author.recipe.all())
        return SubscribeRecipeSerializer(
            recipes,
            many=True).data

    def get_recipes_count(self, subscr):
        return subscr.author.recipes.count()
