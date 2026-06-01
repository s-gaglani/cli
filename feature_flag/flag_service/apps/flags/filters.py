"""
django-filter FilterSet definitions for the flags application.
"""
import django_filters

from .models import Flag, TargetingRule, Variation


class FlagFilter(django_filters.FilterSet):
    """
    Allows filtering flags by:
      - project_id    (exact UUID)
      - environment_key (exact string)
      - is_enabled    (boolean)
      - flag_type     (choice)
    """

    project_id = django_filters.UUIDFilter(field_name="project_id", lookup_expr="exact")
    environment_key = django_filters.CharFilter(
        field_name="environment_key", lookup_expr="exact"
    )
    is_enabled = django_filters.BooleanFilter(field_name="is_enabled")
    flag_type = django_filters.ChoiceFilter(
        field_name="flag_type",
        choices=Flag.FLAG_TYPE_CHOICES,
    )

    class Meta:
        model = Flag
        fields = ["project_id", "environment_key", "is_enabled", "flag_type"]


class VariationFilter(django_filters.FilterSet):
    flag = django_filters.UUIDFilter(field_name="flag__id", lookup_expr="exact")
    is_control = django_filters.BooleanFilter(field_name="is_control")

    class Meta:
        model = Variation
        fields = ["flag", "is_control"]


class TargetingRuleFilter(django_filters.FilterSet):
    flag = django_filters.UUIDFilter(field_name="flag__id", lookup_expr="exact")
    segment_id = django_filters.UUIDFilter(field_name="segment_id", lookup_expr="exact")
    is_active = django_filters.BooleanFilter(field_name="is_active")

    class Meta:
        model = TargetingRule
        fields = ["flag", "segment_id", "is_active"]
