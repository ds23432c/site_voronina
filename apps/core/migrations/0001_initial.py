from django.conf import settings
import apps.core.models as core_models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Calculation",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="название")),
                ("calculation_type", models.CharField(blank=True, max_length=100, verbose_name="тип расчёта")),
                ("inputs", models.JSONField(blank=True, default=dict, verbose_name="входные данные")),
                ("result", models.JSONField(blank=True, default=dict, verbose_name="результат")),
                ("notes", models.TextField(blank=True, verbose_name="примечание")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="обновлено")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="calculations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "расчёт",
                "verbose_name_plural": "расчёты",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="Article",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="заголовок")),
                ("slug", models.SlugField(max_length=255, unique=True, verbose_name="slug")),
                ("content", models.TextField(verbose_name="содержимое")),
                (
                    "category",
                    models.CharField(
                        choices=core_models.ArticleCategory.choices,
                        max_length=32,
                        verbose_name="категория",
                    ),
                ),
                ("cover_url", models.URLField(max_length=500, verbose_name="обложка")),
                ("is_published", models.BooleanField(default=True, verbose_name="опубликовано")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="создано")),
                ("views_count", models.PositiveIntegerField(default=0, verbose_name="просмотры")),
            ],
            options={
                "verbose_name": "статья",
                "verbose_name_plural": "статьи",
                "ordering": ["-created_at"],
            },
        ),
    ]