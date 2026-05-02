# Generated manually for the knowledge app.
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="KnowledgeArticle",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Заголовок")),
                ("slug", models.SlugField(blank=True, max_length=280, unique=True, verbose_name="Slug")),
                ("excerpt", models.CharField(max_length=360, verbose_name="Краткое описание")),
                ("content", models.TextField(verbose_name="Текст статьи")),
                ("cover_url", models.URLField(blank=True, max_length=500, verbose_name="Обложка")),
                ("views_count", models.PositiveIntegerField(default=0, verbose_name="Просмотры")),
                ("is_featured", models.BooleanField(default=False, verbose_name="Рекомендуемая")),
                ("is_published", models.BooleanField(default=True, verbose_name="Опубликовано")),
                ("published_at", models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
            ],
            options={
                "verbose_name": "статья базы знаний",
                "verbose_name_plural": "Статьи базы знаний",
                "ordering": ["-published_at", "-created_at"],
            },
        ),
    ]