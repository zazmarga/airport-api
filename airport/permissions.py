from rest_framework.permissions import BasePermission


class IsAdminAllOrIfAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view):

        if request.method == "DELETE":
            return False

        return bool(
            (
                request.method in ("GET", "HEAD", "OPTIONS")
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )
