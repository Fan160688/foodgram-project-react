from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from .manager import UserManager
from .validators import name_validator


class User(AbstractUser):
    """Модель пользователей."""
    username_validator = UnicodeUsernameValidator()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']

    username = models.CharField(
        max_length=settings.USERNAME_MAX_LENGTH,
        unique=True,
        validators=[name_validator],
        verbose_name='Имя пользователя',
    )
    email = models.EmailField(
        max_length=settings.EMAIL_MAX_LENGTH,
        unique=True,
        verbose_name='Адрес электронной почты',
        error_messages={
            "unique": "Пользователь с таким email уже есть.",
        },
    )
    first_name = models.CharField(
        max_length=settings.NAME_MAX_LENGTH,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=settings.NAME_MAX_LENGTH,
        verbose_name='Фамилия',
    )
    subscribe = models.ManyToManyField(
        'self', through='Follow', symmetrical=False,
        through_fields=('user', 'author')
    )

    objects = UserManager()

    class Meta:
        ordering = ('-pk',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def follow_for(self, obj):
        Follow.objects.get_or_create(
            user=self,
            author=obj
        )

    def unfollow(self, obj):
        Follow.objects.filter(
            user=self,
            author=obj
        ).delete()

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Класс для подписки на авторов"""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follow',
        verbose_name='Автор')

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_follow'
            ),
            models.CheckConstraint(
                name='Ограничение на самоподписку',
                check=~models.Q(user=models.F('author')),
            ),
        ]

    def __str__(self):
        return f'{self.user} {self.author}'
