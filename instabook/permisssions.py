from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrIfAuthenticatedReadOnly(BasePermission):
    def has_permission(self, request, view):
        return bool(
            (
                request.method in SAFE_METHODS
                and request.user
                and request.user.is_authenticated
            )
            or (request.user and request.user.is_staff)
        )


class IsProfileOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of a profile to delete it.
    """

    def has_permission(self, request, view):

        if request.method in SAFE_METHODS:
            return True

        return request.user == view.get_object().user
