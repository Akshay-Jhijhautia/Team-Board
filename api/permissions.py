from rest_framework.permissions import BasePermission

from .models import Company


class IsAdminUser(BasePermission):
    message = "Admin access required."

    def has_permission(self, request, view):
        user = request.user

        return bool(
            user
            and user.is_authenticated
            and hasattr(user, "company")
            and user.company.role == Company.Role.ADMIN
        )
