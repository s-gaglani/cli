"""
Root URL configuration for flag_service.
"""
from django.contrib import admin
from django.urls import include, path

from flag_service.health import HealthCheckView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # Health check — intentionally outside /api/v1/ so load balancers can reach
    # it without routing through an API gateway.
    path("health/", HealthCheckView.as_view(), name="health-check"),

    # Feature flags API
    path("api/v1/", include("apps.flags.urls")),

    # Segments API
    path("api/v1/", include("apps.segments.urls")),
]
