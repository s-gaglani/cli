"""
ViewSets for the flags application.
"""
import logging

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from .filters import FlagFilter, TargetingRuleFilter, VariationFilter
from .models import Flag, TargetingRule, Variation
from .pagination import StandardResultsSetPagination
from .permissions import FlagServicePermission
from .serializers import (
    FlagCreateUpdateSerializer,
    FlagDetailSerializer,
    FlagListSerializer,
    TargetingRuleSerializer,
    VariationSerializer,
)

logger = logging.getLogger(__name__)


class FlagViewSet(ModelViewSet):
    """
    CRUD operations for Feature Flags plus a custom toggle action.

    list:   GET  /api/v1/flags/
    create: POST /api/v1/flags/
    retrieve: GET  /api/v1/flags/{id}/
    update: PUT  /api/v1/flags/{id}/
    partial_update: PATCH /api/v1/flags/{id}/
    destroy: DELETE /api/v1/flags/{id}/
    toggle: POST /api/v1/flags/{id}/toggle/
    """

    queryset = Flag.objects.prefetch_related("variations", "targeting_rules").all()
    permission_classes = [FlagServicePermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = FlagFilter
    search_fields = ["name", "key", "description"]
    ordering_fields = ["created_at", "updated_at", "name", "key"]
    ordering = ["-created_at"]

    def get_serializer_class(self):
        if self.action == "list":
            return FlagListSerializer
        if self.action in ("create", "update", "partial_update"):
            return FlagCreateUpdateSerializer
        return FlagDetailSerializer

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info("Flag created: id=%s key=%s", instance.id, instance.key)

    def perform_update(self, serializer):
        instance = serializer.save()
        logger.info("Flag updated: id=%s key=%s", instance.id, instance.key)

    def perform_destroy(self, instance):
        logger.info("Flag deleted: id=%s key=%s", instance.id, instance.key)
        instance.delete()

    @action(detail=True, methods=["post"], url_path="toggle")
    def toggle_flag(self, request, pk=None):
        """
        POST /api/v1/flags/{id}/toggle/

        Flips the `is_enabled` field and returns the updated flag detail.
        """
        flag = self.get_object()
        flag.is_enabled = not flag.is_enabled
        flag.save(update_fields=["is_enabled", "updated_at"])
        logger.info(
            "Flag toggled: id=%s key=%s is_enabled=%s",
            flag.id,
            flag.key,
            flag.is_enabled,
        )
        serializer = FlagDetailSerializer(flag, context={"request": request})
        return Response(serializer.data, status=status.HTTP_200_OK)


class VariationViewSet(ModelViewSet):
    """
    CRUD operations for Flag Variations.

    list:   GET  /api/v1/variations/
    create: POST /api/v1/variations/
    retrieve: GET  /api/v1/variations/{id}/
    update: PUT  /api/v1/variations/{id}/
    partial_update: PATCH /api/v1/variations/{id}/
    destroy: DELETE /api/v1/variations/{id}/
    """

    queryset = Variation.objects.select_related("flag").all()
    serializer_class = VariationSerializer
    permission_classes = [FlagServicePermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = VariationFilter
    ordering_fields = ["name", "created_at"]
    ordering = ["name"]

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            "Variation created: id=%s flag_id=%s name=%s",
            instance.id,
            instance.flag_id,
            instance.name,
        )

    def perform_destroy(self, instance):
        logger.info("Variation deleted: id=%s name=%s", instance.id, instance.name)
        instance.delete()


class TargetingRuleViewSet(ModelViewSet):
    """
    CRUD operations for Targeting Rules.

    list:   GET  /api/v1/targeting-rules/
    create: POST /api/v1/targeting-rules/
    retrieve: GET  /api/v1/targeting-rules/{id}/
    update: PUT  /api/v1/targeting-rules/{id}/
    partial_update: PATCH /api/v1/targeting-rules/{id}/
    destroy: DELETE /api/v1/targeting-rules/{id}/
    """

    queryset = TargetingRule.objects.select_related("flag", "variation").all()
    serializer_class = TargetingRuleSerializer
    permission_classes = [FlagServicePermission]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = TargetingRuleFilter
    ordering_fields = ["priority", "created_at"]
    ordering = ["priority"]

    def perform_create(self, serializer):
        instance = serializer.save()
        logger.info(
            "TargetingRule created: id=%s flag_id=%s segment_id=%s",
            instance.id,
            instance.flag_id,
            instance.segment_id,
        )

    def perform_destroy(self, instance):
        logger.info("TargetingRule deleted: id=%s", instance.id)
        instance.delete()
