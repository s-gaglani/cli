"""
Serializers for the flags application.
"""
from rest_framework import serializers

from .models import Flag, TargetingRule, Variation


# ---------------------------------------------------------------------------
# Variation
# ---------------------------------------------------------------------------

class VariationSerializer(serializers.ModelSerializer):
    """Full serializer for Variation — used for read and write."""

    class Meta:
        model = Variation
        fields = [
            "id",
            "flag",
            "name",
            "value",
            "is_control",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]


# ---------------------------------------------------------------------------
# TargetingRule
# ---------------------------------------------------------------------------

class TargetingRuleSerializer(serializers.ModelSerializer):
    """Full serializer for TargetingRule — used for read and write."""

    class Meta:
        model = TargetingRule
        fields = [
            "id",
            "flag",
            "segment_id",
            "variation",
            "priority",
            "is_active",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# ---------------------------------------------------------------------------
# Flag — list (lightweight)
# ---------------------------------------------------------------------------

class FlagListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list endpoints."""

    class Meta:
        model = Flag
        fields = [
            "id",
            "project_id",
            "environment_key",
            "name",
            "key",
            "flag_type",
            "is_enabled",
            "rollout_percentage",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]


# ---------------------------------------------------------------------------
# Flag — detail (full + nested relations)
# ---------------------------------------------------------------------------

class FlagDetailSerializer(serializers.ModelSerializer):
    """
    Full detail serializer.  Embeds variations as nested objects and exposes
    targeting_rules_count as a computed integer.
    """

    variations = VariationSerializer(many=True, read_only=True)
    targeting_rules_count = serializers.SerializerMethodField()

    class Meta:
        model = Flag
        fields = [
            "id",
            "project_id",
            "environment_key",
            "name",
            "key",
            "flag_type",
            "description",
            "is_enabled",
            "rollout_percentage",
            "tags",
            "variations",
            "targeting_rules_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def get_targeting_rules_count(self, obj: Flag) -> int:
        return obj.targeting_rules.count()


# ---------------------------------------------------------------------------
# Flag — create / update (writable)
# ---------------------------------------------------------------------------

class FlagCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer used for POST / PUT / PATCH on Flag.
    Validates that rollout_percentage is within [0, 100].
    """

    class Meta:
        model = Flag
        fields = [
            "project_id",
            "environment_key",
            "name",
            "key",
            "flag_type",
            "description",
            "is_enabled",
            "rollout_percentage",
            "tags",
        ]

    def validate_rollout_percentage(self, value: int) -> int:
        if value < 0 or value > 100:
            raise serializers.ValidationError(
                "rollout_percentage must be between 0 and 100 (inclusive)."
            )
        return value

    def validate_key(self, value: str) -> str:
        """Keys must be slug-like — lowercase alphanumeric and hyphens/underscores."""
        import re

        if not re.match(r"^[a-z0-9_-]+$", value):
            raise serializers.ValidationError(
                "Flag key must contain only lowercase letters, digits, hyphens, "
                "or underscores."
            )
        return value
