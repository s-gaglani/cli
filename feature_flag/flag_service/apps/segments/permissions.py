"""
Permission classes for the segments application.

Currently uses AllowAny as a placeholder.  In production replace with an
API-key–based permission class or JWT validation.
"""
from rest_framework.permissions import AllowAny


class SegmentServicePermission(AllowAny):
    """
    Placeholder permission class.

    TODO: replace AllowAny with API key or JWT validation before going to
    production.
    """
