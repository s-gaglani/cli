import logging
from django.db.models import Count
from rest_framework import viewsets

from .models import Project, Environment
from .serializers import (
    ProjectListSerializer,
    ProjectDetailSerializer,
    ProjectCreateUpdateSerializer,
    EnvironmentListSerializer,
    EnvironmentDetailSerializer,
    EnvironmentCreateUpdateSerializer,
)
from .permissions import EnvironmentServicePermission
from .pagination import ProjectPagination, EnvironmentPagination
from .filters import ProjectFilter, EnvironmentFilter

logger = logging.getLogger(__name__)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoints for Projects.
    GET    /api/v1/projects/       — list
    POST   /api/v1/projects/       — create
    GET    /api/v1/projects/{id}/  — retrieve
    PUT    /api/v1/projects/{id}/  — update
    PATCH  /api/v1/projects/{id}/  — partial update
    DELETE /api/v1/projects/{id}/  — destroy
    """
    permission_classes = [EnvironmentServicePermission]
    pagination_class = ProjectPagination
    filterset_class = ProjectFilter
    search_fields = ['name', 'slug', 'description']
    ordering_fields = ['name', 'created_at', 'is_active']
    ordering = ['-created_at']

    def get_queryset(self):
        return (
            Project.objects
            .select_related('organization')
            .prefetch_related('environments')
            .annotate(environment_count=Count('environments'))
            .order_by('-created_at')
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return ProjectCreateUpdateSerializer
        return ProjectDetailSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            "Project created: %s (id=%s) in org=%s",
            instance.name, instance.id, instance.organization_id,
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info("Project updated: %s (id=%s)", instance.name, instance.id)

    def perform_destroy(self, instance):
        logger.info("Project deleted: %s (id=%s)", instance.name, instance.id)
        instance.delete()


class EnvironmentViewSet(viewsets.ModelViewSet):
    """
    CRUD endpoints for Environments.
    GET    /api/v1/environments/       — list
    POST   /api/v1/environments/       — create
    GET    /api/v1/environments/{id}/  — retrieve
    PUT    /api/v1/environments/{id}/  — update
    PATCH  /api/v1/environments/{id}/  — partial update
    DELETE /api/v1/environments/{id}/  — destroy
    """
    permission_classes = [EnvironmentServicePermission]
    pagination_class = EnvironmentPagination
    filterset_class = EnvironmentFilter
    search_fields = ['name', 'key']
    ordering_fields = ['name', 'created_at', 'is_default']
    ordering = ['name']

    def get_queryset(self):
        return (
            Environment.objects
            .select_related('project', 'project__organization')
            .order_by('name')
        )

    def get_serializer_class(self):
        if self.action == 'list':
            return EnvironmentListSerializer
        if self.action in ('create', 'update', 'partial_update'):
            return EnvironmentCreateUpdateSerializer
        return EnvironmentDetailSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            "Environment created: %s (id=%s) in project=%s",
            instance.name, instance.id, instance.project_id,
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info("Environment updated: %s (id=%s)", instance.name, instance.id)

    def perform_destroy(self, instance):
        logger.info("Environment deleted: %s (id=%s)", instance.name, instance.id)
        instance.delete()
