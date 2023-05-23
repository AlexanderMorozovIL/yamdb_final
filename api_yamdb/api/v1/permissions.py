from rest_framework import permissions


class AdminOnly(permissions.BasePermission):
    """Пользователь является супрюзером или админом."""

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_admin
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Просмотр доступен всем пользователям.
    Пользователь является супрюзером или админом.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS or (
                request.user.is_authenticated
                and request.user.is_admin
            )
        )


class AdminModeratorAuthorReadOnly(permissions.BasePermission):
    """
    Просмотр доступен всем пользователям.
    Пользователь является супрюзером, модератором или админом.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_moderator
        )
