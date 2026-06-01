"""
Django admin registrations for the flags application.
"""
from django.contrib import admin

from .models import Flag, TargetingRule, Variation


@admin.register(Flag)
class FlagAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "key",
        "flag_type",
        "environment_key",
        "project_id",
        "is_enabled",
        "rollout_percentage",
        "created_at",
    ]
    list_filter = ["flag_type", "is_enabled", "environment_key"]
    search_fields = ["name", "key", "description", "project_id"]
    readonly_fields = ["id", "created_at", "updated_at"]
    ordering = ["-created_at"]
    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    "id",
                    "project_id",
                    "environment_key",
                    "name",
                    "key",
                    "flag_type",
                )
            },
        ),
        (
            "Configuration",
            {
                "fields": (
                    "description",
                    "is_enabled",
                    "rollout_percentage",
                    "tags",
                )
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )


@admin.register(Variation)
class VariationAdmin(admin.ModelAdmin):
    list_display = ["name", "flag", "is_control", "created_at"]
    list_filter = ["is_control"]
    search_fields = ["name", "flag__key", "flag__name"]
    readonly_fields = ["id", "created_at", "updated_at"]
    raw_id_fields = ["flag"]


@admin.register(TargetingRule)
class TargetingRuleAdmin(admin.ModelAdmin):
    list_display = ["flag", "segment_id", "variation", "priority", "is_active", "created_at"]
    list_filter = ["is_active"]
    search_fields = ["flag__key", "flag__name", "segment_id"]
    readonly_fields = ["id", "created_at"]
    raw_id_fields = ["flag", "variation"]
    ordering = ["flag", "priority"]
