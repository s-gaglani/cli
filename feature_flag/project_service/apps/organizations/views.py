import logging
from django.db.models import Count
from rest_framework import viewsets, status
from rest_framework.response import Response

from .models import Organization, APIKey
from .serializers import (
    OrganizationListSerializer,
    OrganizationDetailSerializer,
    OrganizationCreateUpdateSerializer,
    APIKeyListSerializer,
    APIKeyCreateSerializer,
    APIKeyDetailSerializer,
)
from .permissions import ProjectServicePermission
from .pagination import OrganizationPagination, APIKeyPagination
from .filters import OrganizationFilter, APIKeyFilter

logger = logging.getLogger(__name__)


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoints for Organizations.
    GET    /api/v1/organizations/       — list
    POST   /api/v1/organizations/       — create
    GET    /api/v1/organizations/{id}/  — retrieve
    PUT    /api/v1/organizations/{id}/  — update
    PATCH  /api/v1/organizations/{id}/  — partial update
    DELETE /api/v1/organizations/{id}/  — destroy
    """
    permission_classes = [ProjectServicePermission]
    pagination_class = OrganizationPagination
    filterset_class = OrganizationFilter
    search_fields = ['name', 'slug']
    ordering_fields = ['name', 'created_at', 'plan']
    ordering = ['-created_at']

    def get_queryset(self):
        return Organization.objects.annotate(
            project_count=Count('projects')
        ).order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return OrganizationListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return OrganizationCreateUpdateSerializer
        return OrganizationDetailSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info("Organization created: %s (id=%s)", instance.name, instance.id)

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info("Organization updated: %s (id=%s)", instance.name, instance.id)

    def perform_destroy(self, instance):
        logger.info("Organization deleted: %s (id=%s)", instance.name, instance.id)
        instance.delete()


class APIKeyViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoints for APIKeys.
    GET    /api/v1/api-keys/       — list
    POST   /api/v1/api-keys/       — create
    GET    /api/v1/api-keys/{id}/  — retrieve
    PUT    /api/v1/api-keys/{id}/  — update
    PATCH  /api/v1/api-keys/{id}/  — partial update
    DELETE /api/v1/api-keys/{id}/  — destroy
    """
    permission_classes = [ProjectServicePermission]
    pagination_class = APIKeyPagination
    filterset_class = APIKeyFilter
    search_fields = ['name', 'prefix']
    ordering_fields = ['name', 'created_at', 'is_active']
    ordering = ['-created_at']

    def get_queryset(self):
        return APIKey.objects.select_related('organization').order_by('-created_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return APIKeyListSerializer
        if self.action == 'create':
            return APIKeyCreateSerializer
        return APIKeyDetailSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            "APIKey created: %s (prefix=%s) for org=%s",
            instance.name, instance.prefix, instance.organization_id,
        )

    def perform_destroy(self, instance):
        logger.info("APIKey deleted: %s (id=%s)", instance.name, instance.id)
        instance.delete()
