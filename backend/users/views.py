from django.shortcuts import get_object_or_404
from djoser.serializers import SetPasswordSerializer
from djoser.views import UserViewSet
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Subscribe, User
from .serializers import (SubscribeSerializer,
                          CustomUserSerializer)


class UserViewSet(UserViewSet):
    "Получение списка пользователей и создание пользователей"
    queryset = User.objects.all()

    def get_serializer_class(self):
        if self.action == 'set_password':
            return SetPasswordSerializer
        if self.action == 'subscribe' or self.action == 'subscriptions':
            return SubscribeSerializer
        return CustomUserSerializer

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=[permissions.IsAuthenticated]
    )
    def me(self, request):
        """ Текущий пользователь """
        serializer = self.get_serializer(request.user)
        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        """ На кого подписан пользователь """
        user = request.user
        queryset = Subscribe.objects.filter(user=user)
        pages = self.paginate_queryset(queryset)
        serializer = self.get_serializer(
            pages, many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(methods=('POST', 'DELETE'), detail=True)
    def subscribe(self, request, pk):
        """ Подписаться/отписаться от пользователя """
        author = get_object_or_404(User, id=pk)
        if request.method != 'POST':
            request.user.subscribe.remove(author)
            return Response(status=status.HTTP_204_NO_CONTENT)
        if not request.user.subscribe.filter(id=pk).exists():
            request.user.subscribe.add(author)
            serializer = self.serializer_class(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {'errors': 'Вы уже подписаны на данного пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )
        