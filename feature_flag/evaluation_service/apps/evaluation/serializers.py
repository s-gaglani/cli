"""
Serializers for the evaluation app.
"""
from rest_framework import serializers
from .models import EvaluationLog


class EvaluateRequestSerializer(serializers.Serializer):
    """Serializer for single flag evaluation request."""
    project_id = serializers.UUIDField()
    environment_key = serializers.CharField(max_length=50)
    flag_key = serializers.CharField(max_length=100)
    user_key = serializers.CharField(max_length=255)
    attributes = serializers.DictField(
        child=serializers.JSONField(),
        required=False,
        default=dict,
    )

    def validate_environment_key(self, value):
        if not value.strip():
            raise serializers.ValidationError("environment_key cannot be blank.")
        return value.strip()

    def validate_flag_key(self, value):
        if not value.strip():
            raise serializers.ValidationError("flag_key cannot be blank.")
        return value.strip()

    def validate_user_key(self, value):
        if not value.strip():
            raise serializers.ValidationError("user_key cannot be blank.")
        return value.strip()


class EvaluateBulkRequestSerializer(serializers.Serializer):
    """Serializer for bulk flag evaluation request."""
    project_id = serializers.UUIDField()
    environment_key = serializers.CharField(max_length=50)
    flag_keys = serializers.ListField(
        child=serializers.CharField(max_length=100),
        min_length=1,
        max_length=100,
    )
    user_key = serializers.CharField(max_length=255)
    attributes = serializers.DictField(
        child=serializers.JSONField(),
        required=False,
        default=dict,
    )

    def validate_environment_key(self, value):
        if not value.strip():
            raise serializers.ValidationError("environment_key cannot be blank.")
        return value.strip()

    def validate_flag_keys(self, value):
        cleaned = [k.strip() for k in value if k.strip()]
        if not cleaned:
            raise serializers.ValidationError("flag_keys must contain at least one non-empty key.")
        return cleaned

    def validate_user_key(self, value):
        if not value.strip():
            raise serializers.ValidationError("user_key cannot be blank.")
        return value.strip()


class EvaluationResultSerializer(serializers.Serializer):
    """Serializer for a single evaluation result."""
    flag_key = serializers.CharField()
    value = serializers.JSONField(allow_null=True)
    reason = serializers.CharField()
    evaluated_at = serializers.DateTimeField()


class EvaluationLogSerializer(serializers.ModelSerializer):
    """Serializer for EvaluationLog model."""

    class Meta:
        model = EvaluationLog
        fields = [
            'id',
            'project_id',
            'environment_key',
            'flag_key',
            'user_key',
            'result_value',
            'reason',
            'evaluated_at',
        ]
        read_only_fields = fields
