from rest_framework import serializers
from .models import Organization, APIKey


class OrganizationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views."""

    class Meta:
        model = Organization
        fields = ['id', 'name', 'slug', 'plan', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrganizationDetailSerializer(serializers.ModelSerializer):
    """Full serializer with annotated project_count for detail views."""
    project_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = [
            'id', 'name', 'slug', 'plan', 'is_active',
            'project_count', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_project_count(self, obj):
        # Use annotated value if present (set by ViewSet), else do a live count
        if hasattr(obj, 'project_count'):
            return obj.project_count
        return obj.projects.count()


class OrganizationCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer used for create and update operations."""

    class Meta:
        model = Organization
        fields = ['name', 'slug', 'plan']

    def validate_slug(self, value):
        if value and not value.replace('-', '').isalnum():
            raise serializers.ValidationError(
                "Slug may only contain letters, numbers, and hyphens."
            )
        return value.lower()


# ---------------------------------------------------------------------------
# APIKey serializers
# ---------------------------------------------------------------------------

class APIKeyListSerializer(serializers.ModelSerializer):
    """List view — never exposes the full key."""
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = APIKey
        fields = ['id', 'name', 'prefix', 'is_active', 'created_at', 'organization']
        read_only_fields = ['id', 'prefix', 'created_at']


class APIKeyCreateSerializer(serializers.ModelSerializer):
    """Create serializer — accepts full key and organization FK."""
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all()
    )

    class Meta:
        model = APIKey
        fields = ['name', 'key', 'organization']

    def validate_key(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Key must be at least 8 characters long.")
        return value


class APIKeyDetailSerializer(serializers.ModelSerializer):
    """Detail view — exposes full key (use with caution)."""
    organization = OrganizationListSerializer(read_only=True)

    class Meta:
        model = APIKey
        fields = [
            'id', 'name', 'key', 'prefix', 'is_active',
            'organization', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'prefix', 'created_at', 'updated_at']
