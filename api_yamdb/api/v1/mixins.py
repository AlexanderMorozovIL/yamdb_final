from django.db.models import prefetch_related_objects
from rest_framework.mixins import (
    CreateModelMixin, DestroyModelMixin,
    ListModelMixin, RetrieveModelMixin
)
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet


class CategoryGenreModelMixin(
    CreateModelMixin,
    ListModelMixin,
    DestroyModelMixin,
    GenericViewSet
):
    """Класс MixinSet для категориев и жанров."""

    pass


class ModelViewSetWithoutPUT(
    CreateModelMixin,
    ListModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    GenericViewSet
):
    """Набор представлений допускает все методы, кроме PUT."""

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        queryset = self.filter_queryset(self.get_queryset())
        if queryset._prefetch_related_lookups:
            instance._prefetched_objects_cache = {}
            prefetch_related_objects(
                [instance], *queryset._prefetch_related_lookups
            )
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()
