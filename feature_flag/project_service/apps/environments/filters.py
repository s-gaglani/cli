import django_filters
from .models import Project, Environment


class ProjectFilter(django_filters.FilterSet):
    """Filter set for Project model."""
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name contains')
    slug = django_filters.CharFilter(lookup_expr='iexact', label='Slug (exact, case-insensitive)')
    organization = django_filters.UUIDFilter(field_name='organization__id', label='Organization ID')
    organization_slug = django_filters.CharFilter(
        field_name='organization__slug',
        lookup_expr='iexact',
        label='Organization slug',
    )
    is_active = django_filters.BooleanFilter()
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Project
        fields = [
            'name', 'slug', 'organization', 'organization_slug',
            'is_active', 'created_after', 'created_before',
        ]


class EnvironmentFilter(django_filters.FilterSet):
    """Filter set for Environment model."""
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name contains')
    key = django_filters.CharFilter(lookup_expr='iexact', label='Key (exact, case-insensitive)')
    project = django_filters.UUIDFilter(field_name='project__id', label='Project ID')
    project_slug = django_filters.CharFilter(
        field_name='project__slug',
        lookup_expr='iexact',
        label='Project slug',
    )
    is_default = django_filters.BooleanFilter()
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Environment
        fields = [
            'name', 'key', 'project', 'project_slug',
            'is_default', 'created_after', 'created_before',
        ]
