from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsBusinessOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return hasattr(request.user, "business") and obj == request.user.business


class IsBusiness(BasePermission):
    def has_permission(self, request, view):
        return hasattr(request.user, "business")


class IsClientOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True

        return hasattr(request.user, "client") and obj == request.user.client
