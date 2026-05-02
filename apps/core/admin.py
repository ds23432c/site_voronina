from django.contrib import admin

from .models import Article, Calculation


@admin.register(Calculation)
class CalculationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "calculation_type", "created_at")
    list_filter = ("calculation_type", "created_at")
    search_fields = ("title", "user__email", "notes")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "is_published", "created_at", "views_count")
    list_filter = ("category", "is_published", "created_at")
    search_fields = ("title", "content", "category")
    readonly_fields = ("created_at", "views_count")
    prepopulated_fields = {"slug": ("title",)}