"""
Pagination for the segments application.

Re-exports the shared pagination class from apps.flags so that each app is
self-contained if imported standalone.
"""
from apps.flags.pagination import StandardResultsSetPagination  # noqa: F401

__all__ = ["StandardResultsSetPagination"]
