"""
Health check endpoint for project_service.
Returns service status, name, and version.
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


class HealthCheckView(APIView):
    """
    GET /health/
    Returns a simple health-check payload.
    Used by load balancers, orchestrators, and Docker HEALTHCHECK.
    """
    permission_classes = [AllowAny]
    authentication_classes = []  # no auth required for health checks

    def get(self, request, *args, **kwargs):
        data = {
            'status': 'ok',
            'service': 'project-service',
            'version': '1.0.0',
        }
        return Response(data, status=status.HTTP_200_OK)
