"""
ViewSets for the segments application.
"""
import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.viewsets import ModelViewSet

from .filters import SegmentFilter
from .models import Segment
from .pagination import StandardResultsSetPagination
from .permissions import SegmentServicePermission
from .serializers import (
    SegmentCreateUpdateSerializer,
    SegmentDetailSerializer,
    SegmentListSerializer,
)

logger = logging.getLogger(__name__)


class SegmentViewSet(ModelViewSet):
    """
    CRUD operations for Segments.

    list:   GET  /api/v1/segments/
    create: POST /api/v1/segments/
    retrieve: GET  /api/v1/segments/{id}/
    update: PUT  /api/v1/segments/{id}/
    partial_update: PATCH /api/v1/segments/{id}/
    destroy: DELETE /api/v1/segments/{id}/
    """

    queryset = Segment.objects.all()
    permission_classes = [SegmentServicePermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = SegmentFilter
    search_fields = ["name", "description"]
    ordering_fields = ["created_at", "updated_at", "name"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return SegmentListSerializer
        if self.action in ("create", "update", "partial_update"):
            return SegmentCreateUpdateSerializer
        return SegmentDetailSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            "Segment created: id=%s name=%s project_id=%s",
            instance.id,
            instance.name,
            instance.project_id,
        )

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info(
            "Segment updated: id=%s name=%s",
            instance.id,
            instance.name,
        )

    def perform_destroy(self, instance):
        logger.info("Segment deleted: id=%s name=%s", instance.id, instance.name)
        instance.delete()
