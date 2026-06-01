"""
Custom DRF permissions for the evaluation app.
"""
from rest_framework.permissions import BasePermission


class AllowAny(BasePermission):
    """
    Allow any access. This is the default for the evaluation service
    since it is intended to be called by SDK clients.

    In production, you may want to add SDK key validation here.
    """

    def has_permission(self, request, view):
        return True


class HasSDKKey(BasePermission):
    """
    Optional: Validate an SDK key header for service-to-service authentication.
    Set X-SDK-Key header on requests.

    Activate by setting REQUIRE_SDK_KEY=True in settings and
    configuring SDK_KEYS as a list/set of valid keys.
    """

    def has_permission(self, request, view):
        from django.conf import settings

        if not getattr(settings, 'REQUIRE_SDK_KEY', False):
            return True

        sdk_key = request.META.get('HTTP_X_SDK_KEY', '').strip()
        valid_keys = getattr(settings, 'SDK_KEYS', [])
        return sdk_key in valid_keys
