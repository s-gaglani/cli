import uuid

from django.db import models


class Flag(models.Model):
    FLAG_TYPE_CHOICES = [
        ("boolean", "Boolean"),
        ("string", "String"),
        ("number", "Number"),
        ("json", "JSON"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_id = models.UUIDField(db_index=True)          # external ref to project_service
    environment_key = models.CharField(max_length=50, db_index=True)
    name = models.CharField(max_length=255)
    key = models.CharField(max_length=100, db_index=True)
    flag_type = models.CharField(
        max_length=20, choices=FLAG_TYPE_CHOICES, default="boolean"
    )
    description = models.TextField(blank=True)
    is_enabled = models.BooleanField(default=False)
    rollout_percentage = models.PositiveSmallIntegerField(default=0)  # 0-100
    tags = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = [["project_id", "environment_key", "key"]]
        indexes = [
            models.Index(fields=["project_id", "environment_key"]),
        ]

    def __str__(self) -> str:
        return f"{self.name} ({self.key}) — {self.environment_key}"


class Variation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flag = models.ForeignKey(Flag, on_delete=models.CASCADE, related_name="variations")
    name = models.CharField(max_length=100)
    value = models.JSONField()
    is_control = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return f"{self.flag.key} — {self.name}"


class TargetingRule(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    flag = models.ForeignKey(
        Flag, on_delete=models.CASCADE, related_name="targeting_rules"
    )
    segment_id = models.UUIDField(db_index=True)  # external ref to segment
    variation = models.ForeignKey(
        Variation, on_delete=models.CASCADE, related_name="targeting_rules"
    )
    priority = models.PositiveSmallIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["priority"]

    def __str__(self) -> str:
        return (
            f"Rule(flag={self.flag.key}, segment={self.segment_id}, "
            f"priority={self.priority})"
        )
