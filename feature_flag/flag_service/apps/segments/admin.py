"""
Django admin registrations for the segments application.
"""
from django.contrib import admin

from .models import Segment


@admin.register(Segment)
class SegmentAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "project_id",
        "created_at",
        "updated_at",
    ]
    list_filter = ["project_id"]
    search_fields = ["name", "description", "project_id"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-created_at"]
    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    "id",
                    "project_id",
                    "name",
                )
            },
        ),
        (
            "Details",
            {
                "fields": (
                    "description",
                    "rules",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )
