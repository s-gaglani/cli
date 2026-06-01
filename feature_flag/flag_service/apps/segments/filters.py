"""
django-filter FilterSet definitions for the segments application.
"""
import django_filters

from .models import Segment


class SegmentFilter(django_filters.FilterSet):
    """
    Allows filtering segments by:
      - project_id (exact UUID)
      - name       (case-insensitive contains)
    """

    project_id = django_filters.UUIDFilter(field_name="project_id", lookup_expr="exact")
    name = django_filters.CharFilter(field_name="name", lookup_expr="icontains")

    class Meta:
        model = Segment
        fields = ["project_id", "name"]
