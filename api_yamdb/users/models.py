from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.db import models

from .validators import validate_username


class User(AbstractUser):
    """
    Модель пользователя с дополнительными полями
    биография и роль.
    """

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'
    ROLE_CHOICES = (
        (USER, 'user'),
        (MODERATOR, 'moderator'),
        (ADMIN, 'admin')
    )
    email = models.EmailField(
        unique=True,
        max_length=settings.EMAIL_MAX_LENGTH,
        verbose_name='Электронная почта'
    )
    bio = models.TextField(
        blank=True,
        verbose_name='Биография пользователя'
    )
    role = models.CharField(
        choices=ROLE_CHOICES,
        default=USER,
        max_length=20,
        verbose_name='Роль пользователя'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique_user_email'
            )
        ]
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def clean(self):
        super().clean()
        try:
            validate_username(self.username)
        except ValidationError as e:
            raise ValidationError({'username': e})

    @property
    def is_user(self):
        """Пользователь по умолчанию."""
        return self.role == User.USER

    @property
    def is_moderator(self):
        """Пользователь с правами модератора."""
        return self.role == User.MODERATOR

    @property
    def is_admin(self):
        """Пользователь с правами админа и суперпользователей."""
        return (
            self.role == User.ADMIN
            or self.is_superuser
        )
