"""
API views for the evaluation app.
"""
import logging
from datetime import datetime, timezone

from django.conf import settings
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .clients import FlagServiceClient
from .services import evaluate_flag, evaluate_flags_bulk
from .serializers import (
    EvaluateRequestSerializer,
    EvaluateBulkRequestSerializer,
    EvaluationResultSerializer,
    EvaluationLogSerializer,
)
from .models import EvaluationLog
from .filters import EvaluationLogFilter
from .pagination import StandardResultsPagination

logger = logging.getLogger(__name__)


def _log_evaluation_async(project_id, environment_key, flag_key, user_key, result):
    """
    Non-blocking helper to persist an EvaluationLog entry.
    Errors are swallowed to avoid impacting the evaluation response.
    """
    try:
        EvaluationLog.objects.create(
            project_id=project_id,
            environment_key=environment_key,
            flag_key=flag_key,
            user_key=user_key,
            result_value=result.get("value"),
            reason=result.get("reason", "DEFAULT"),
        )
    except Exception as exc:  # noqa: BLE001
        logger.warning("Failed to persist EvaluationLog: %s", exc)


class EvaluateView(APIView):
    """
    POST /api/v1/evaluate/

    Evaluate a single feature flag for a user context.
    """

    def post(self, request):
        serializer = EvaluateRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        project_id = data["project_id"]
        environment_key = data["environment_key"]
        flag_key = data["flag_key"]
        user_key = data["user_key"]
        attributes = data.get("attributes", {})

        # Fetch flag configuration from flag_service
        client = FlagServiceClient()
        flag_data = client.get_flag(project_id, environment_key, flag_key)

        # Evaluate the flag
        result = evaluate_flag(flag_data, user_key, attributes)
        result["flag_key"] = flag_key
        result["evaluated_at"] = datetime.now(timezone.utc).isoformat()

        # Persist evaluation log (non-blocking, errors swallowed)
        _log_evaluation_async(
            project_id=project_id,
            environment_key=environment_key,
            flag_key=flag_key,
            user_key=user_key,
            result=result,
        )

        return Response(result, status=status.HTTP_200_OK)


class EvaluateBulkView(APIView):
    """
    POST /api/v1/evaluate/bulk/

    Evaluate multiple feature flags for a user context in a single request.
    """

    def post(self, request):
        serializer = EvaluateBulkRequestSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        data = serializer.validated_data
        project_id = data["project_id"]
        environment_key = data["environment_key"]
        flag_keys = data["flag_keys"]
        user_key = data["user_key"]
        attributes = data.get("attributes", {})
        evaluated_at = datetime.now(timezone.utc).isoformat()

        # Fetch all flag configurations from flag_service
        client = FlagServiceClient()
        flags_data = client.get_flags_bulk(project_id, environment_key, flag_keys)

        # Evaluate all flags
        results = evaluate_flags_bulk(flags_data, flag_keys, user_key, attributes)

        # Attach evaluated_at timestamp and persist logs
        response_data = []
        for result in results:
            result["evaluated_at"] = evaluated_at
            _log_evaluation_async(
                project_id=project_id,
                environment_key=environment_key,
                flag_key=result["flag_key"],
                user_key=user_key,
                result=result,
            )
            response_data.append(result)

        return Response(response_data, status=status.HTTP_200_OK)


class EvaluationLogListView(ListAPIView):
    """
    GET /api/v1/logs/

    List EvaluationLog entries with optional filtering.
    Supports filtering by project_id, flag_key, user_key, and reason.
    """
    queryset = EvaluationLog.objects.all()
    serializer_class = EvaluationLogSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = EvaluationLogFilter
    pagination_class = StandardResultsPagination
    ordering_fields = ['evaluated_at', 'flag_key', 'user_key', 'reason']
    ordering = ['-evaluated_at']
