from rest_framework.permissions import BasePermission, IsAuthenticated
from tune.models import Tune

class IsOwner(BasePermission):
    """Custom permission class to allow only tune owners to edit them."""

    def has_object_permission(self, request, view, obj):
        """Return True if permission is granted to the tune owner."""
        if isinstance(obj, Tune):
            return obj.added_by == request.user
        return obj.added_by == request.user

class AllowOptionsAuthentication(IsAuthenticated):
    def has_permission(self, request, view):
        if request.method == 'OPTIONS':
            return True
        return request.user and request.user.is_authenticated