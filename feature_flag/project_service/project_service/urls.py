"""
Root URL configuration for project_service.
"""
from django.contrib import admin
from django.urls import path, include
from project_service.health import HealthCheckView

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Health check
    path('health/', HealthCheckView.as_view(), name='health-check'),

    # API v1
    path('api/v1/', include('apps.organizations.urls')),
    path('api/v1/', include('apps.environments.urls')),
]
