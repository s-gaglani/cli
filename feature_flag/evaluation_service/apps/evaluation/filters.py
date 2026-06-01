"""
django-filter FilterSets for the evaluation app.
"""
import django_filters
from .models import EvaluationLog


class EvaluationLogFilter(django_filters.FilterSet):
    """
    Filter for EvaluationLog list endpoint.

    Supported query parameters:
        - project_id  (exact UUID)
        - flag_key    (exact or case-insensitive contains)
        - user_key    (exact or case-insensitive contains)
        - reason      (exact choice)
        - evaluated_at_after   (datetime gte)
        - evaluated_at_before  (datetime lte)
    """
    project_id = django_filters.UUIDFilter(field_name='project_id', lookup_expr='exact')
    flag_key = django_filters.CharFilter(field_name='flag_key', lookup_expr='iexact')
    flag_key__contains = django_filters.CharFilter(field_name='flag_key', lookup_expr='icontains')
    user_key = django_filters.CharFilter(field_name='user_key', lookup_expr='exact')
    user_key__contains = django_filters.CharFilter(field_name='user_key', lookup_expr='icontains')
    reason = django_filters.ChoiceFilter(
        field_name='reason',
        choices=EvaluationLog.REASON_CHOICES,
    )
    evaluated_at_after = django_filters.DateTimeFilter(
        field_name='evaluated_at',
        lookup_expr='gte',
    )
    evaluated_at_before = django_filters.DateTimeFilter(
        field_name='evaluated_at',
        lookup_expr='lte',
    )
    environment_key = django_filters.CharFilter(
        field_name='environment_key',
        lookup_expr='iexact',
    )

    class Meta:
        model = EvaluationLog
        fields = [
            'project_id',
            'flag_key',
            'user_key',
            'reason',
            'environment_key',
        ]
