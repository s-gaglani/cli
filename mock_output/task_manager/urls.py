from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", include("task_manager.health")),
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/tasks/", include("apps.tasks.urls")),
]
