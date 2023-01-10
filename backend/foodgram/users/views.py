from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from .models import Subscribe, User
from .serializers import (SubscribeSerializer, UserCreateSerializer,
                          UserSerializer)


def check_required_fields(request, fields):
    error_required_fields = {}

    for field_name in fields:
        field_value = request.data.get(field_name)
        if not field_value:
            error_required_fields[field_name] = [
                'Missing field or empty value.'
            ]

    if error_required_fields:
        raise ValidationError(detail=error_required_fields)


class SignupViewSet(viewsets.ViewSet):
    def create(self, request):
        required_fields = ('username', 'email',)
        check_required_fields(request, required_fields)

        username = request.data.get('username')
        email = request.data.get('email')

        user = User.objects.filter(
            username=username, email=email
        )

        if user.exists():
            found_user = user[0]
            found_user.email_user(
                'Registration confirmation code from YAMDB',
                f'{found_user.confirmation_code}'
            )
            return Response(
                data={'username': username, 'email': email},
                status=status.HTTP_200_OK
            )

        serializer = UserSerializer(data=request.data)

        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            user.email_user(
                'Registration confirmation code from YAMDB',
                f'{user.confirmation_code}'
            )

        response_data = {'username': username, 'email': email}
        return Response(data=response_data, status=status.HTTP_200_OK)


class UserViewSet(viewsets.ModelViewSet):
    "Получение списка пользователей и создание пользователей"
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action == 'subscribe' or self.action == 'subscriptions':
            return SubscribeSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[permissions.IsAuthenticated,]
    )
    def me(self, request):
        """ Текущий пользователь """
        serializer = self.get_serializer(request.user)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['POST'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def set_password(self, request, *args, **kwargs):
        """ Изменения пароля """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.request.user.set_password(
            serializer.validated_data.get('new_password')
        )
        self.request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        permission_classes=[permissions.IsAuthenticated,]
    )
    def subscriptions(self, request):
        """ На кого подписан пользователь """
        user = request.user
        queryset = Subscribe.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            pages, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=('POST', 'DELETE'), detail=False,
            url_path=r'(?P<id>\d+)/subscribe')
    def subscribe(self, request, id):
        """ Подписаться/отписаться от пользователя """
        user = request.user
        author = get_object_or_404(User, id=id)
        if user == author:
            return Response(
                {'errors': 'Нельзя подписаться на самого себя!'},
                status=status.HTTP_400_BAD_REQUEST)
        if request.method == 'DELETE':
            object = Subscribe.objects.filter(
                author=author, user=user).first()
            if object is None:
                return Response(
                    {'errors': 'Вы не подписаны на этого автора!'},
                    status=status.HTTP_400_BAD_REQUEST)
            object.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if Subscribe.objects.filter(author=author, user=user).exists():
            return Response(
                    {'errors': 'Вы уже подписаны на этого автора!'},
                    status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Subscribe.objects.create(
            user=user, author=author)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
