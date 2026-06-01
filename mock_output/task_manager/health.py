from django.http import JsonResponse
from django.urls import path

VERSION = "1.0.0"
SERVICE_NAME = "task-manager"


def health_check(request):
    return JsonResponse({"status": "ok", "service": SERVICE_NAME, "version": VERSION})


urlpatterns = [path("", health_check)]
