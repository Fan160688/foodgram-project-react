from rest_framework import serializers

from recipes.models import Recipe

from .models import Subscribe, User


class SubscribeRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class UserCreateSerializer(serializers.ModelSerializer):
    "Сериализатор создания пользователей"

    def validate_username(self, username):
        if username.lower() == 'me':
            raise serializers.ValidationError(
                'Недопустимое имя пользователя!'
            )
        if not username.islower():
            raise serializers.ValidationError(
                'username должен состоять из строчных букв!'
            )
        return username

    def validate_first_name(self, first_name):
        if not first_name.istitle():
            raise serializers.ValidationError(
                'Имя должно быть с заглавной буквы!'
            )
        return first_name

    def validate_last_name(self, last_name):
        if not last_name.istitle():
            raise serializers.ValidationError(
                'Фамилия должна быть с заглавной буквы!'
            )
        return last_name

    class Meta:
        model = User
        fields = (
            'id', 'email', 'username',
            'first_name', 'last_name', 'password',)


class UserSerializer(serializers.ModelSerializer):
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
        request = self.context['request']
        user = request.user
        if user.is_anonymous:
            return False
        return Subscribe.objects.filter(user=user, author=obj).exists()


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
