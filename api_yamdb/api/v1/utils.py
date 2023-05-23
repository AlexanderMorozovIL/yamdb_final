from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail


def send_confirmation_code(user):
    """Отправляет код для регистрации на почту."""
    confirmation_code = default_token_generator.make_token(user)
    send_mail(
        subject='Регистрация на Yamdb',
        message=(
            'Для завершения регистрации на Yamdb отправьте запрос '
            f'с именем пользователя {user.username} и '
            f'кодом подтверждения {confirmation_code} '
            'на эндпойнт /api/v1/auth/token/.'
        ),
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email]
    )
