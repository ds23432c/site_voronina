from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Organization, User


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ("name", "owner", "organization_type", "tax_system", "created_at")
    list_filter = ("organization_type", "tax_system", "created_at")
    search_fields = ("name", "inn", "email", "owner__email")
    readonly_fields = ("created_at", "updated_at")