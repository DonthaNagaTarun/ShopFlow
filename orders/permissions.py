from rest_framework.permissions import BasePermission


class IsOrderOwner(BasePermission):
    """
    Users can access only their own orders.
    """

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user


class IsStaffOrAdmin(BasePermission):
    """
    Only staff and admin users can manage order status.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ['staff', 'admin']
        )