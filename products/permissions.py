from rest_framework.permissions import BasePermission


class IsStaffOrAdmin(BasePermission):
    """
    Staff and admin can create and update products.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ['staff', 'admin']
        )


class IsAdmin(BasePermission):
    """
    Only admin users can delete products.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == 'admin'
        )