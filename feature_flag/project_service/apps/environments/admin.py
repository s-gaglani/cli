from django.contrib import admin
from .models import Project, Environment


class EnvironmentInline(admin.TabularInline):
    model = Environment
    extra = 0
    readonly_fields = ['id', 'created_at', 'updated_at']
    fields = ['name', 'key', 'color', 'is_default', 'created_at']
    show_change_link = True


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'organization', 'is_active', 'created_at']
    list_filter = ['is_active', 'organization', 'created_at']
    search_fields = ['name', 'slug', 'organization__name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['-created_at']
    raw_id_fields = ['organization']
    inlines = [EnvironmentInline]
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'slug', 'organization', 'is_active'),
        }),
        ('Details', {
            'fields': ('description',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Environment)
class EnvironmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'key', 'project', 'color', 'is_default', 'created_at']
    list_filter = ['is_default', 'project__organization', 'created_at']
    search_fields = ['name', 'key', 'project__name', 'project__organization__name']
    readonly_fields = ['id', 'created_at', 'updated_at']
    ordering = ['name']
    raw_id_fields = ['project']
    fieldsets = (
        (None, {
            'fields': ('id', 'name', 'key', 'project', 'color', 'is_default'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
