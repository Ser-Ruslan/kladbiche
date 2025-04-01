from rest_framework import permissions


class IsAdminUser(permissions.BasePermission):
    """
    Разрешение, которое проверяет, является ли пользователь администратором.
    """
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Разрешение, которое проверяет, является ли пользователь владельцем объекта или администратором.
    """
    def has_object_permission(self, request, view, obj):
        # Администраторы могут редактировать любые объекты
        if request.user.is_staff:
            return True
            
        # Проверяем, является ли пользователь владельцем
        return obj.user == request.user
