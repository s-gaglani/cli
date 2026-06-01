"""
URL configuration for evaluation_service project.
"""
from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from .health import health_check

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', health_check, name='health-check'),
    path('api/v1/', include('apps.evaluation.urls', namespace='evaluation')),
    path('', RedirectView.as_view(url='/health/', permanent=False)),
]
