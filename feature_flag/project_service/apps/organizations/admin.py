from django.contrib import admin
from .models import Organization, APIKey


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'plan', 'is_active', 'created_at', 'updated_at']
    list_filter = ['plan', 'is_active', 'created_at']
    search_fields = ['name', 'slug']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'slug', 'plan', 'is_active'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['name', 'prefix', 'organization', 'is_active', 'created_at']
    list_filter = ['is_active', 'organization', 'created_at']
    search_fields = ['name', 'prefix', 'organization__name']
    readonly_fields = ['id', 'prefix', 'created_at', 'updated_at']
    ordering = ['-created_at']
    raw_id_fields = ['organization']
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'key', 'prefix', 'organization', 'is_active'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
