"""
Canned mock response used when --mock is passed.
Simulates a Claude response for a simple Task Management API
so the full parse → write pipeline can be tested without an API key.
"""

MOCK_RESPONSE = """\
## Architecture Decision Summary

Single Django project with two apps: `tasks` and `users`.
This is a straightforward CRUD application — no microservices needed.
The `users` app handles user profiles; `tasks` owns task lifecycle.

<<<FILE: manage.py>>>
#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings.local")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError("Couldn't import Django.") from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
<<<ENDFILE>>>

<<<FILE: requirements.txt>>>
Django>=4.2,<5.0
djangorestframework>=3.14
django-filter>=23.0
django-cors-headers>=4.0
python-decouple>=3.8
psycopg2-binary>=2.9
gunicorn>=21.0
<<<ENDFILE>>>

<<<FILE: .env.example>>>
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=task_manager
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
CORS_ALLOWED_ORIGINS=http://localhost:3000
<<<ENDFILE>>>

<<<FILE: .gitignore>>>
__pycache__/
*.pyc
*.pyo
.env
*.sqlite3
.DS_Store
staticfiles/
media/
<<<ENDFILE>>>

<<<FILE: Dockerfile>>>
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["gunicorn", "task_manager.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
<<<ENDFILE>>>

<<<FILE: docker-compose.yml>>>
version: "3.9"

services:
  db:
    image: postgres:15
    environment:
      POSTGRES_DB: task_manager
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    command: python manage.py runserver 0.0.0.0:8000
    volumes:
      - .:/app
    ports:
      - "8000:8000"
    env_file:
      - .env
    depends_on:
      - db

volumes:
  postgres_data:
<<<ENDFILE>>>

<<<FILE: .dockerignore>>>
__pycache__
*.pyc
.env
.git
<<<ENDFILE>>>

<<<FILE: task_manager/__init__.py>>>
<<<ENDFILE>>>

<<<FILE: task_manager/settings/__init__.py>>>
<<<ENDFILE>>>

<<<FILE: task_manager/settings/base.py>>>
from pathlib import Path
from decouple import config, Csv

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", default=False, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost", cast=Csv())

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "django_filters",
    "corsheaders",
]

LOCAL_APPS = [
    "apps.users",
    "apps.tasks",
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "task_manager.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "task_manager.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="task_manager"),
        "USER": config("DB_USER", default="postgres"),
        "PASSWORD": config("DB_PASSWORD", default="postgres"),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticatedOrReadOnly",
    ],
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
}

CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", default="http://localhost:3000", cast=Csv())

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {"format": "{levelname} {asctime} {module} {message}", "style": "{"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "verbose"},
    },
    "root": {"handlers": ["console"], "level": "INFO"},
    "loggers": {
        "django": {"handlers": ["console"], "level": "INFO", "propagate": False},
    },
}
<<<ENDFILE>>>

<<<FILE: task_manager/settings/local.py>>>
from .base import *

DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES["default"]["NAME"] = "task_manager_local"
<<<ENDFILE>>>

<<<FILE: task_manager/settings/production.py>>>
from .base import *

DEBUG = False
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
<<<ENDFILE>>>

<<<FILE: task_manager/urls.py>>>
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", include("task_manager.health")),
    path("api/v1/users/", include("apps.users.urls")),
    path("api/v1/tasks/", include("apps.tasks.urls")),
]
<<<ENDFILE>>>

<<<FILE: task_manager/health.py>>>
from django.http import JsonResponse
from django.urls import path

VERSION = "1.0.0"
SERVICE_NAME = "task-manager"


def health_check(request):
    return JsonResponse({"status": "ok", "service": SERVICE_NAME, "version": VERSION})


urlpatterns = [path("", health_check)]
<<<ENDFILE>>>

<<<FILE: task_manager/wsgi.py>>>
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings.production")
application = get_wsgi_application()
<<<ENDFILE>>>

<<<FILE: task_manager/asgi.py>>>
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "task_manager.settings.production")
application = get_asgi_application()
<<<ENDFILE>>>

<<<FILE: apps/__init__.py>>>
<<<ENDFILE>>>

<<<FILE: apps/users/__init__.py>>>
<<<ENDFILE>>>

<<<FILE: apps/users/apps.py>>>
from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.users"
<<<ENDFILE>>>

<<<FILE: apps/users/models.py>>>
from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date_joined"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email or self.username
<<<ENDFILE>>>

<<<FILE: apps/users/serializers.py>>>
from rest_framework import serializers
from .models import User


class UserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "date_joined"]
        read_only_fields = ["id", "date_joined"]


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "bio", "avatar_url", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]
<<<ENDFILE>>>

<<<FILE: apps/users/views.py>>>
from rest_framework import viewsets, permissions
from .models import User
from .serializers import UserListSerializer, UserDetailSerializer


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all().order_by("-date_joined")
    permission_classes = [permissions.IsAdminUser]

    def get_serializer_class(self):
        if self.action == "list":
            return UserListSerializer
        return UserDetailSerializer
<<<ENDFILE>>>

<<<FILE: apps/users/urls.py>>>
from rest_framework.routers import DefaultRouter
from .views import UserViewSet

router = DefaultRouter()
router.register(r"", UserViewSet, basename="user")

urlpatterns = router.urls
<<<ENDFILE>>>

<<<FILE: apps/users/admin.py>>>
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ["username", "email", "is_staff", "date_joined"]
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profile", {"fields": ("bio", "avatar_url")}),
    )
<<<ENDFILE>>>

<<<FILE: apps/users/permissions.py>>>
from rest_framework.permissions import BasePermission


class IsSelfOrAdmin(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_staff or obj == request.user
<<<ENDFILE>>>

<<<FILE: apps/users/filters.py>>>
import django_filters
from .models import User


class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = {"username": ["icontains"], "email": ["icontains"]}
<<<ENDFILE>>>

<<<FILE: apps/users/pagination.py>>>
from rest_framework.pagination import PageNumberPagination


class UserPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
<<<ENDFILE>>>

<<<FILE: apps/users/migrations/__init__.py>>>
<<<ENDFILE>>>

<<<FILE: apps/users/tests/__init__.py>>>
<<<ENDFILE>>>

<<<FILE: apps/users/tests/test_models.py>>>
from django.test import TestCase
from apps.users.models import User


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="testuser", email="test@example.com", password="pass")

    def test_user_creation(self):
        self.assertEqual(self.user.username, "testuser")
        self.assertEqual(str(self.user), self.user.email)
<<<ENDFILE>>>

<<<FILE: apps/users/tests/test_serializers.py>>>
from django.test import TestCase
from apps.users.models import User
from apps.users.serializers import UserDetailSerializer


class UserSerializerTest(TestCase):
    def test_serializer_fields(self):
        user = User.objects.create_user(username="u", email="u@example.com", password="p")
        data = UserDetailSerializer(user).data
        self.assertIn("email", data)
        self.assertIn("username", data)
<<<ENDFILE>>>

<<<FILE: apps/users/tests/test_views.py>>>
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from apps.users.models import User


class UserViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.admin = User.objects.create_superuser(username="admin", email="a@example.com", password="pass")
        self.client.force_authenticate(user=self.admin)

    def test_list_users(self):
        response = self.client.get("/api/v1/users/")
        self.assertEqual(response.status_code, 200)
<<<ENDFILE>>>

<<<FILE: apps/tasks/__init__.py>>>
<<<ENDFILE>>>

<<<FILE: apps/tasks/apps.py>>>
from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.tasks"
<<<ENDFILE>>>

<<<FILE: apps/tasks/models.py>>>
from django.db import models
from django.conf import settings


class Task(models.Model):
    class Priority(models.TextChoices):
        LOW = "low", "Low"
        MEDIUM = "medium", "Medium"
        HIGH = "high", "High"

    class Status(models.TextChoices):
        TODO = "todo", "To Do"
        IN_PROGRESS = "in_progress", "In Progress"
        DONE = "done", "Done"

    title = models.CharField(max_length=255, db_index=True)
    description = models.TextField(blank=True)
    priority = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.TODO, db_index=True)
    due_date = models.DateField(null=True, blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tasks",
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Task"
        verbose_name_plural = "Tasks"

    def __str__(self):
        return self.title
<<<ENDFILE>>>

<<<FILE: apps/tasks/serializers.py>>>
from rest_framework import serializers
from .models import Task


class TaskListSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Task
        fields = ["id", "title", "priority", "status", "due_date", "owner_username", "created_at"]
        read_only_fields = ["id", "created_at"]


class TaskDetailSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source="owner.username", read_only=True)

    class Meta:
        model = Task
        fields = [
            "id", "title", "description", "priority", "status",
            "due_date", "owner", "owner_username", "assignee",
            "created_at", "updated_at",
        ]
        read_only_fields = ["id", "owner", "created_at", "updated_at"]


class TaskCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ["title", "description", "priority", "status", "due_date", "assignee"]

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)
<<<ENDFILE>>>

<<<FILE: apps/tasks/views.py>>>
from rest_framework import viewsets, permissions
from .models import Task
from .serializers import TaskListSerializer, TaskDetailSerializer, TaskCreateSerializer


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            Task.objects.select_related("owner", "assignee")
            .filter(owner=self.request.user)
            .order_by("-created_at")
        )

    def get_serializer_class(self):
        if self.action == "list":
            return TaskListSerializer
        if self.action == "create":
            return TaskCreateSerializer
        return TaskDetailSerializer
<<<ENDFILE>>>

<<<FILE: apps/tasks/urls.py>>>
from rest_framework.routers import DefaultRouter
from .views import TaskViewSet

router = DefaultRouter()
router.register(r"", TaskViewSet, basename="task")

urlpatterns = router.urls
<<<ENDFILE>>>

<<<FILE: apps/tasks/admin.py>>>
from django.contrib import admin
from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ["title", "status", "priority", "owner", "due_date", "created_at"]
    list_filter = ["status", "priority"]
    search_fields = ["title", "description"]
    raw_id_fields = ["owner", "assignee"]
<<<ENDFILE>>>

<<<FILE: apps/tasks/permissions.py>>>
from rest_framework.permissions import BasePermission


class IsTaskOwner(BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user
<<<ENDFILE>>>

<<<FILE: apps/tasks/filters.py>>>
import django_filters
from .models import Task


class TaskFilter(django_filters.FilterSet):
    class Meta:
        model = Task
        fields = {
            "status": ["exact"],
            "priority": ["exact"],
            "due_date": ["exact", "lte", "gte"],
        }
<<<ENDFILE>>>

<<<FILE: apps/tasks/pagination.py>>>
from rest_framework.pagination import PageNumberPagination


class TaskPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100
<<<ENDFILE>>>

<<<FILE: apps/tasks/migrations/__init__.py>>>
<<<ENDFILE>>>

<<<FILE: apps/tasks/tests/__init__.py>>>
<<<ENDFILE>>>

<<<FILE: apps/tasks/tests/test_models.py>>>
from django.test import TestCase
from apps.users.models import User
from apps.tasks.models import Task


class TaskModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="u", email="u@example.com", password="p")
        self.task = Task.objects.create(title="Write tests", owner=self.user)

    def test_task_creation(self):
        self.assertEqual(self.task.title, "Write tests")
        self.assertEqual(self.task.status, Task.Status.TODO)
        self.assertEqual(str(self.task), "Write tests")
<<<ENDFILE>>>

<<<FILE: apps/tasks/tests/test_serializers.py>>>
from django.test import TestCase
from apps.users.models import User
from apps.tasks.models import Task
from apps.tasks.serializers import TaskListSerializer


class TaskSerializerTest(TestCase):
    def test_list_serializer_fields(self):
        user = User.objects.create_user(username="u", email="u@example.com", password="p")
        task = Task.objects.create(title="My task", owner=user)
        data = TaskListSerializer(task).data
        self.assertIn("title", data)
        self.assertIn("status", data)
<<<ENDFILE>>>

<<<FILE: apps/tasks/tests/test_views.py>>>
from django.test import TestCase
from rest_framework.test import APIClient
from apps.users.models import User
from apps.tasks.models import Task


class TaskViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username="u", email="u@example.com", password="p")
        self.client.force_authenticate(user=self.user)
        Task.objects.create(title="Task 1", owner=self.user)

    def test_list_own_tasks(self):
        response = self.client.get("/api/v1/tasks/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 1)

    def test_create_task(self):
        payload = {"title": "New task", "priority": "high"}
        response = self.client.post("/api/v1/tasks/", payload)
        self.assertEqual(response.status_code, 201)
<<<ENDFILE>>>

<<<FILE: README.md>>>
# Task Manager API

Production-grade Django REST Framework backend for task management.

## Quick Start

```bash
cp .env.example .env
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Docker

```bash
docker-compose up --build
```

## Endpoints

| Method | URL | Description |
|--------|-----|-------------|
| GET | /health/ | Health check |
| GET/POST | /api/v1/tasks/ | List / create tasks |
| GET/PUT/DELETE | /api/v1/tasks/{id}/ | Task detail |
| GET | /api/v1/users/ | List users (admin only) |

## Settings

| Env Var | Description |
|---------|-------------|
| SECRET_KEY | Django secret key |
| DEBUG | True/False |
| DB_NAME / DB_USER / DB_PASSWORD / DB_HOST / DB_PORT | PostgreSQL |
| CORS_ALLOWED_ORIGINS | Comma-separated frontend origins |
<<<ENDFILE>>>

<<<EXTENSION_NOTES>>>
- Add JWT authentication (simplejwt) in phase 2
- Expand TaskViewSet with shared/team tasks using a Team model
- Add email notifications via Celery + Django email backend
- Add assignee filter to TaskFilter for team views
<<<END>>>
"""
