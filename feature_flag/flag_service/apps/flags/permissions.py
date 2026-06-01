"""
Permission classes for the flags application.

Currently uses AllowAny as a placeholder.  In production replace this with an
API-key–based permission class, e.g.:

    from rest_framework_api_key.permissions import HasAPIKey

    class FlagServiceAPIKeyPermission(HasAPIKey):
        ...

Or implement a custom JWT / service-to-service token validation here.
"""
from rest_framework.permissions import AllowAny


class FlagServicePermission(AllowAny):
    """
    Placeholder permission class.

    TODO: replace AllowAny with API key or JWT validation before going to
    production.
    """
