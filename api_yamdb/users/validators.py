import re

from django.core.exceptions import ValidationError


def validate_username(value):
    """
    Нельзя использовать имя пользователя me.

    Допускается использовать только буквы, цифры и символы.
    """
    pattern = re.compile(r'^[a-zA-Z][a-zA-Z0-9-_\.]{1,20}$')

    if pattern.fullmatch(value) is None:
        match = re.split(pattern, value)
        symbol = ''.join(match)
        raise ValidationError(f'Некорректные символы в username: {symbol}')
    if value == 'me':
        raise ValidationError(
            ('Имя пользователя не может быть <me>.'),
            params={'value': value},
        )
    return value
