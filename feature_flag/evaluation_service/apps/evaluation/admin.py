"""
Django admin configuration for the evaluation app.
"""
from django.contrib import admin
from .models import EvaluationLog


@admin.register(EvaluationLog)
class EvaluationLogAdmin(admin.ModelAdmin):
    """Admin interface for EvaluationLog. Read-only audit trail."""

    list_display = [
        'flag_key',
        'user_key',
        'project_id',
        'environment_key',
        'reason',
        'result_value',
        'evaluated_at',
    ]
    list_filter = [
        'reason',
        'environment_key',
        'evaluated_at',
    ]
    search_fields = [
        'flag_key',
        'user_key',
        'project_id',
    ]
    readonly_fields = [
        'id',
        'project_id',
        'environment_key',
        'flag_key',
        'user_key',
        'result_value',
        'reason',
        'evaluated_at',
    ]
    ordering = ['-evaluated_at']
    date_hierarchy = 'evaluated_at'

    def has_add_permission(self, request):
        """Evaluation logs are created by the service, not manually."""
        return False

    def has_change_permission(self, request, obj=None):
        """Evaluation logs are immutable audit records."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete evaluation logs."""
        return request.user.is_superuser
