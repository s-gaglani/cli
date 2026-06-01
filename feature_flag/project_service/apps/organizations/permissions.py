"""
Placeholder permission classes for project_service — organizations app.

TODO: Replace AllowAny with a real permission class once authentication is
      implemented.  The intended flow is:
        1. Each inbound request carries either a JWT Bearer token (user-facing)
           or an API key in the X-API-Key header (service-to-service).
        2. A custom authentication backend validates the credential and attaches
           the resolved identity to request.user / request.auth.
        3. The permission class below then enforces role-based access control
           (e.g. org members can read; org admins can write).

Example future implementation:
    class IsOrganizationMember(BasePermission):
        def has_permission(self, request, view):
            return bool(request.user and request.user.is_authenticated)

        def has_object_permission(self, request, view, obj):
            return obj.members.filter(user=request.user).exists()
"""
from rest_framework.permissions import AllowAny


class ProjectServicePermission(AllowAny):
    """
    Currently allows unrestricted access.
    Replace with JWT / API-key authentication in production.
    """
    pass
