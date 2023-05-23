from django.contrib.auth.tokens import default_token_generator
from django.db.models import Avg
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken
from reviews.models import Category, Genre, Review, Title
from users.models import User

from .filters import TitleFilter
from .mixins import CategoryGenreModelMixin, ModelViewSetWithoutPUT
from .permissions import (AdminModeratorAuthorReadOnly, AdminOnly,
                          IsAdminOrReadOnly)
from .serializers import (CategorySerializer, CommentsSerializer,
                          GenreSerializer, GetTokenSerializer,
                          ReviewSerializer, SignSerializer,
                          TitleCreateSerializer, TitleGetSerializer,
                          UserSerializer)
from .utils import send_confirmation_code


class UserViewSet(ModelViewSetWithoutPUT):
    """
    Вьюсет модели User.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AdminOnly,)
    lookup_field = 'username'
    filter_backends = (SearchFilter, )
    search_fields = ('username', )

    @action(
        methods=['GET', 'PATCH'],
        detail=False,
        permission_classes=(IsAuthenticated,),
        url_path='me'
    )
    def get_current_user_info(self, request):
        user = request.user
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                user,
                data=request.data,
                partial=True
            )
            serializer.is_valid(raise_exception=True)
            serializer.save(role=request.user.role)
        else:
            serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class SignView(APIView):
    """
    Регистрация нового пользователя.
    Отправка кода для подтверждения регистрации на email.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SignSerializer(data=request.data, partial=True)
        if User.objects.filter(
            username=request.data.get('username'),
            email=request.data.get('email')
        ).exists():
            user = User.objects.get(
                username=request.data.get('username')
            )
            send_confirmation_code(user)
            return Response(
                {'confirmation_code': 'код подтверждения обновлен'},
                status=status.HTTP_200_OK
            )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        user = User.objects.get(
            username=serializer.data['username'],
            email=request.data['email']
        )
        send_confirmation_code(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class GetTokenView(APIView):
    """
    Получение JWT-токена по confirmation code.
    """

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.validated_data.get('username')
        confirmation_code = serializer.validated_data['confirmation_code']
        user = get_object_or_404(User, username=username)
        if default_token_generator.check_token(user, confirmation_code):
            token = AccessToken.for_user(user)
            return Response(
                {'token': token},
                status=status.HTTP_200_OK
            )
        return Response(
            {
                "confirmation_code": (
                    "Неверный код доступа "
                    f"{confirmation_code}"
                )
            },
            status=status.HTTP_400_BAD_REQUEST
        )


class ReviewViewSet(ModelViewSetWithoutPUT):
    """Вьюсет для отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = [
        AdminModeratorAuthorReadOnly,
    ]

    def get_queryset(self):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            id=self.kwargs.get('title_id')
        )
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(ModelViewSetWithoutPUT):
    """Вьюсет для комментариев."""

    serializer_class = CommentsSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
        AdminModeratorAuthorReadOnly
    ]

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            id=self.kwargs.get('review_id')
        )
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)


class CategoryViewSet(CategoryGenreModelMixin):
    """Вьюсет для категорий."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'


class GenreViewSet(CategoryGenreModelMixin):
    """Вьюсет для жанров."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (SearchFilter,)
    search_fields = ('name', )
    lookup_field = 'slug'


class TitleViewSet(ModelViewSetWithoutPUT):
    """Вьюсет для произведения."""

    queryset = Title.objects.select_related('category').annotate(
        Avg('reviews__score')
    ).order_by('name')
    serializer_class = TitleGetSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = TitleFilter
    search_fields = ['name']
    ordering_fields = ['name', 'year']

    def get_serializer_class(self):
        if self.action in ('retrieve', 'list'):
            return TitleGetSerializer
        return TitleCreateSerializer
