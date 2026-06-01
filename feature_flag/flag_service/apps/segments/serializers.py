"""
Serializers for the segments application.
"""
from rest_framework import serializers

from .models import Segment

# Valid operators that rules may use
VALID_OPERATORS = {"eq", "neq", "in", "not_in", "contains", "not_contains", "gt", "gte", "lt", "lte"}


class SegmentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list endpoints."""

    class Meta:
        model = Segment
        fields = [
            "id",
            "project_id",
            "name",
            "description",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


class SegmentDetailSerializer(serializers.ModelSerializer):
    """Full detail serializer including rules."""

    class Meta:
        model = Segment
        fields = [
            "id",
            "project_id",
            "name",
            "description",
            "rules",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


class SegmentCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating segments.
    Validates the structure of ``rules``.
    """

    class Meta:
        model = Segment
        fields = [
            "project_id",
            "name",
            "description",
            "rules",
        ]

    def validate_rules(self, value):
        """
        Validate that rules is a list of dicts, each with the required keys
        ``attribute``, ``operator``, and ``value``.
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("rules must be a JSON array.")

        for index, rule in enumerate(value):
            if not isinstance(rule, dict):
                raise serializers.ValidationError(
                    f"Rule at index {index} must be a JSON object."
                )
            missing = {"attribute", "operator", "value"} - rule.keys()
            if missing:
                raise serializers.ValidationError(
                    f"Rule at index {index} is missing required keys: {missing}."
                )
            if rule["operator"] not in VALID_OPERATORS:
                raise serializers.ValidationError(
                    f"Rule at index {index} has invalid operator '{rule['operator']}'. "
                    f"Valid operators are: {sorted(VALID_OPERATORS)}."
                )
            if not isinstance(rule["attribute"], str) or not rule["attribute"].strip():
                raise serializers.ValidationError(
                    f"Rule at index {index} 'attribute' must be a non-empty string."
                )

        return value
