"""
URL routing for the flags application.

Registers:
    /api/v1/flags/
    /api/v1/flags/{id}/
    /api/v1/flags/{id}/toggle/
    /api/v1/variations/
    /api/v1/variations/{id}/
    /api/v1/targeting-rules/
    /api/v1/targeting-rules/{id}/
"""
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import FlagViewSet, TargetingRuleViewSet, VariationViewSet

router = DefaultRouter()
router.register(r"flags", FlagViewSet, basename="flag")
router.register(r"variations", VariationViewSet, basename="variation")
router.register(r"targeting-rules", TargetingRuleViewSet, basename="targeting-rule")

urlpatterns = [
    path("", include(router.urls)),
]
