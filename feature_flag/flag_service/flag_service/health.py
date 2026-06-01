"""
Health check endpoint for flag_service.

GET /health/ -> {"status": "ok", "service": "flag-service", "version": "1.0.0"}
"""
from rest_framework.response import Response
from rest_framework.views import APIView


class HealthCheckView(APIView):
    """
    Simple health check.  Used by load balancers and container orchestrators
    to determine whether the service is alive.
    """

    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        return Response(
            {
                "status": "ok",
                "service": "flag-service",
                "version": "1.0.0",
            }
        )
