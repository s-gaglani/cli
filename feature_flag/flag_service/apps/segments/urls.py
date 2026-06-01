"""
URL routing for the segments application.

Registers:
    /api/v1/segments/
    /api/v1/segments/{id}/
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import SegmentViewSet

router = DefaultRouter()
router.register(r"segments", SegmentViewSet, basename="segment")

urlpatterns = [
    path("", include(router.urls)),
]
