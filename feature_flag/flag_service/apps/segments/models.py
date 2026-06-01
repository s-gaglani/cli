import uuid

from django.db import models


class Segment(models.Model):
    """
    A Segment represents a group of users that share certain attributes.

    The ``rules`` field stores a list of rule objects, each describing an
    attribute-based condition:

        [
          {"attribute": "country", "operator": "eq",  "value": "US"},
          {"attribute": "plan",    "operator": "in",  "value": ["pro", "enterprise"]},
          {"attribute": "age",     "operator": "gte", "value": 18}
        ]

    Supported operators (evaluated client-side / by the evaluation engine):
        eq, neq, in, not_in, contains, not_contains, gt, gte, lt, lte
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_id = models.UUIDField(db_index=True)  # external ref to project_service
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    rules = models.JSONField(default=list)  # list of rule objects: [{attribute, operator, value}]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return f"{self.name} (project={self.project_id})"
