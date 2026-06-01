from rest_framework import serializers
from .models import Project, Environment
from apps.organizations.models import Organization


# ---------------------------------------------------------------------------
# Environment serializers
# ---------------------------------------------------------------------------

class EnvironmentListSerializer(serializers.ModelSerializer):
    """Lightweight environment serializer for list views."""

    class Meta:
        model = Environment
        fields = ['id', 'name', 'key', 'color', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']


class EnvironmentDetailSerializer(serializers.ModelSerializer):
    """Full environment serializer including project FK."""
    project = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Environment
        fields = [
            'id', 'name', 'key', 'color', 'is_default',
            'project', 'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class EnvironmentCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for create / update of environments."""
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = Environment
        fields = ['name', 'key', 'color', 'is_default', 'project']

    def validate_color(self, value):
        if not value.startswith('#') or len(value) not in (4, 7):
            raise serializers.ValidationError(
                "Color must be a valid hex color code (e.g. #fff or #6366f1)."
            )
        return value

    def validate_key(self, value):
        return value.lower().replace(' ', '-')


# ---------------------------------------------------------------------------
# Project serializers
# ---------------------------------------------------------------------------

class ProjectListSerializer(serializers.ModelSerializer):
    """Lightweight project serializer for list views."""
    organization = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Project
        fields = ['id', 'name', 'slug', 'organization', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProjectDetailSerializer(serializers.ModelSerializer):
    """Full project serializer with nested environments."""
    organization = serializers.PrimaryKeyRelatedField(read_only=True)
    environments = EnvironmentListSerializer(many=True, read_only=True)
    environment_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            'id', 'name', 'slug', 'description', 'is_active',
            'organization', 'environments', 'environment_count',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_environment_count(self, obj):
        if hasattr(obj, 'environment_count'):
            return obj.environment_count
        return obj.environments.count()


class ProjectCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer for create / update of projects."""
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all()
    )

    class Meta:
        model = Project
        fields = ['name', 'slug', 'description', 'is_active', 'organization']

    def validate_slug(self, value):
        if value and not value.replace('-', '').replace('_', '').isalnum():
            raise serializers.ValidationError(
                "Slug may only contain letters, numbers, hyphens, and underscores."
            )
        return value.lower()

    def validate(self, attrs):
        organization = attrs.get('organization') or getattr(self.instance, 'organization', None)
        slug = attrs.get('slug') or getattr(self.instance, 'slug', None)
        if organization and slug:
            qs = Project.objects.filter(organization=organization, slug=slug)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError(
                    {'slug': 'A project with this slug already exists in this organization.'}
                )
        return attrs
