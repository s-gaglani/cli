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
