from rest_framework.permissions import BasePermission
from ..models import User


class IsAdminRoleUser(BasePermission):
    """
    Allows access only to admin role users.
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.role == User.ADMIN)
