# Generated manually for the forum app.
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="ForumCategory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, unique=True, verbose_name="Название")),
                ("slug", models.SlugField(blank=True, max_length=140, unique=True, verbose_name="Slug")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
            ],
            options={
                "verbose_name": "категория форума",
                "verbose_name_plural": "Категории форума",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="ForumPost",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=255, verbose_name="Заголовок")),
                ("slug", models.SlugField(blank=True, max_length=280, unique=True, verbose_name="Slug")),
                ("content", models.TextField(verbose_name="Содержание")),
                ("likes_count", models.PositiveIntegerField(default=0, verbose_name="Лайки")),
                ("views_count", models.PositiveIntegerField(default=0, verbose_name="Просмотры")),
                ("is_published", models.BooleanField(default=True, verbose_name="Опубликовано")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                ("updated_at", models.DateTimeField(auto_now=True, verbose_name="Обновлено")),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="forum_posts",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор",
                    ),
                ),
            ],
            options={
                "verbose_name": "тема форума",
                "verbose_name_plural": "Темы форума",
                "ordering": ["-created_at"],
            },
        ),
        migrations.CreateModel(
            name="ForumComment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("content", models.TextField(verbose_name="Комментарий")),
                ("likes_count", models.PositiveIntegerField(default=0, verbose_name="Лайки")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                (
                    "author",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="forum_comments",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Автор",
                    ),
                ),
                (
                    "post",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="comments",
                        to="forum.forumpost",
                        verbose_name="Тема",
                    ),
                ),
            ],
            options={
                "verbose_name": "комментарий форума",
                "verbose_name_plural": "Комментарии форума",
                "ordering": ["created_at"],
            },
        ),
        migrations.AddField(
            model_name="forumpost",
            name="categories",
            field=models.ManyToManyField(blank=True, related_name="posts", to="forum.forumcategory", verbose_name="Категории"),
        ),
    ]