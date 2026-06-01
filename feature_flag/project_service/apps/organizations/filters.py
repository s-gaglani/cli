import django_filters
from .models import Organization, APIKey


class OrganizationFilter(django_filters.FilterSet):
    """Filter set for Organization model."""
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name contains')
    slug = django_filters.CharFilter(lookup_expr='iexact', label='Slug (exact, case-insensitive)')
    plan = django_filters.ChoiceFilter(choices=Organization.PLAN_CHOICES)
    is_active = django_filters.BooleanFilter()
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Organization
        fields = ['name', 'slug', 'plan', 'is_active', 'created_after', 'created_before']


class APIKeyFilter(django_filters.FilterSet):
    """Filter set for APIKey model."""
    name = django_filters.CharFilter(lookup_expr='icontains', label='Name contains')
    organization = django_filters.UUIDFilter(field_name='organization__id')
    organization_slug = django_filters.CharFilter(
        field_name='organization__slug',
        lookup_expr='iexact',
        label='Organization slug',
    )
    is_active = django_filters.BooleanFilter()
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = APIKey
        fields = ['name', 'organization', 'organization_slug', 'is_active']
