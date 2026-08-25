from rest_framework.permissions import BasePermission


class IsAdminRole(BasePermission):
    message = "Access forbidden: insufficient permissions"

    def has_permission(self, request, view):
        user = request.user
        return bool(user and getattr(user, "is_authenticated", False) and user.role == "admin")
