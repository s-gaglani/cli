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
