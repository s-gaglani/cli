"""
Health check endpoint for evaluation_service.
"""
import json
from django.http import JsonResponse
from django.db import connection
from django.db.utils import OperationalError


def health_check(request):
    """
    Simple health check endpoint.
    Returns service status and basic metadata.
    """
    health_data = {
        "status": "ok",
        "service": "evaluation-service",
        "version": "1.0.0",
    }

    # Optional: check database connectivity
    try:
        connection.ensure_connection()
        health_data["database"] = "ok"
    except OperationalError:
        health_data["database"] = "unavailable"
        health_data["status"] = "degraded"

    status_code = 200 if health_data["status"] in ("ok", "degraded") else 503
    return JsonResponse(health_data, status=status_code)
