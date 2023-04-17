from rest_framework import permissions


class IsOwnerOnly(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        # Permission only to the original  user
        return obj.author == request.user
