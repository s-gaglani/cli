from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, APIKeyViewSet

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'api-keys', APIKeyViewSet, basename='apikey')

urlpatterns = [
    path('', include(router.urls)),
]
