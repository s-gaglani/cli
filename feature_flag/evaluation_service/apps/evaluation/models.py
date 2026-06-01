"""
Models for the evaluation app.
"""
import uuid
from django.db import models


class EvaluationLog(models.Model):
    """
    Log entry for each flag evaluation performed by this service.
    Provides an audit trail and analytics foundation.
    """
    REASON_CHOICES = [
        ('DEFAULT', 'Default'),
        ('TARGETING', 'Targeting'),
        ('ROLLOUT', 'Rollout'),
        ('DISABLED', 'Disabled'),
        ('ROLLOUT_EXCLUDED', 'Rollout Excluded'),
        ('FLAG_NOT_FOUND', 'Flag Not Found'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_id = models.UUIDField(db_index=True)
    environment_key = models.CharField(max_length=50, db_index=True)
    flag_key = models.CharField(max_length=100, db_index=True)
    user_key = models.CharField(max_length=255, db_index=True)
    result_value = models.JSONField()
    reason = models.CharField(
        max_length=50,
        default='DEFAULT',
        choices=REASON_CHOICES,
    )
    evaluated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-evaluated_at']
        indexes = [
            models.Index(fields=['project_id', 'environment_key', 'flag_key']),
            models.Index(fields=['user_key', 'evaluated_at']),
        ]
        verbose_name = 'Evaluation Log'
        verbose_name_plural = 'Evaluation Logs'

    def __str__(self):
        return (
            f"EvaluationLog({self.flag_key} / {self.user_key} / "
            f"{self.reason} @ {self.evaluated_at})"
        )
