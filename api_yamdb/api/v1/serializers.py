from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import serializers

from reviews.models import Category, Comments, Genre, Review, Title

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для User."""

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role'
        )
        validators = [
            serializers.UniqueTogetherValidator(
                queryset=User.objects.all(), fields=['email', 'username']
            )
        ]

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Имя пользователя не может быть me.'
            )

        return value

    def validate(self, data):
        email = data.get('email', None)
        if User.objects.filter(email=email).exists():
            if data['username'] != User.objects.get(email=email).username:
                raise serializers.ValidationError(
                    'Этот email уже используется!'
                )

        return super().validate(data)


class SignSerializer(UserSerializer):
    """Сериализатор для регистрации."""

    class Meta(UserSerializer.Meta):
        fields = ('email', 'username')
        model = User


class GetTokenSerializer(serializers.Serializer):
    """Сериализатор для получения токена."""

    confirmation_code = serializers.CharField(required=True)
    username = serializers.CharField(required=True)


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для Category."""

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для Genre."""

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleGetSerializer(serializers.ModelSerializer):
    """Сериализатор для чтения Title."""

    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer(read_only=True)
    rating = serializers.IntegerField(read_only=True)

    class Meta:
        fields = (
            'id',
            'name',
            'year',
            'rating',
            'description',
            'genre',
            'category'
        )
        model = Title


class TitleCreateSerializer(serializers.ModelSerializer):
    """Сериализатор для создания Title."""

    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug'
    )
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        many=True,
        slug_field='slug'
    )

    class Meta:
        fields = ('id', 'name', 'year', 'description', 'genre', 'category')
        model = Title

    def validate_year(self, value):
        if 1900 > value > timezone.now().year:
            raise serializers.ValidationError(
                " год выпуска не может быть"
                "больше текущего"
            )
        return value


class ReviewSerializer(serializers.ModelSerializer):
    """Сериалайзер для отзывов."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = (
            'id',
            'text',
            'author',
            'score',
            'pub_date'
        )
        read_only_fields = (
            'id', 'author', 'pub_date',
        )

    def validate(self, data):
        request = self.context['request']
        author = request.user
        title_id = self.context.get('view').kwargs.get('title_id')
        title = get_object_or_404(Title, pk=title_id)
        if (
            request.method == 'POST'
            and Review.objects.filter(title=title, author=author).exists()
        ):
            raise ValidationError('Может существовать только один отзыв!')
        return data


class CommentsSerializer(serializers.ModelSerializer):
    """Сериалайзер для комментариев."""

    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comments
        fields = (
            'id',
            'text',
            'author',
            'pub_date'
        )
        read_only_fields = (
            'id', 'author', 'pub_date',
        )
