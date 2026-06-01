"""
Placeholder permission classes for project_service — environments app.

TODO: Replace AllowAny with a real permission class once authentication is
      implemented.  The intended flow is:
        1. Each inbound request carries either a JWT Bearer token (user-facing)
           or an API key in the X-API-Key header (service-to-service).
        2. A custom authentication backend validates the credential and attaches
           the resolved identity to request.user / request.auth.
        3. The permission class below then enforces project-level access control
           (e.g. project members can read environments; admins can mutate).

Example future implementation:
    class IsProjectMember(BasePermission):
        def has_object_permission(self, request, view, obj):
            project = obj if isinstance(obj, Project) else obj.project
            return project.organization.members.filter(user=request.user).exists()
"""
from rest_framework.permissions import AllowAny


class EnvironmentServicePermission(AllowAny):
    """
    Currently allows unrestricted access.
    Replace with JWT / API-key authentication in production.
    """
    pass
