from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class ForumCategory(models.Model):
    name = models.CharField("Название", max_length=120, unique=True)
    slug = models.SlugField("Slug", max_length=140, unique=True, blank=True)
    description = models.TextField("Описание", blank=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "категория форума"
        verbose_name_plural = "Категории форума"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name) or "category"
            slug = base_slug
            index = 1
            while ForumCategory.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                index += 1
                slug = f"{base_slug}-{index}"
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ForumPost(models.Model):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="forum_posts",
        verbose_name="Автор",
    )
    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField("Slug", max_length=280, unique=True, blank=True)
    content = models.TextField("Содержание")
    categories = models.ManyToManyField(
        ForumCategory,
        related_name="posts",
        blank=True,
        verbose_name="Категории",
    )
    likes_count = models.PositiveIntegerField("Лайки", default=0)
    views_count = models.PositiveIntegerField("Просмотры", default=0)
    is_published = models.BooleanField("Опубликовано", default=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "тема форума"
        verbose_name_plural = "Темы форума"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "post"
            slug = base_slug
            index = 1
            while ForumPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                index += 1
                slug = f"{base_slug}-{index}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("forum:detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title


class ForumComment(models.Model):
    post = models.ForeignKey(
        ForumPost,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name="Тема",
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="forum_comments",
        verbose_name="Автор",
    )
    content = models.TextField("Комментарий")
    likes_count = models.PositiveIntegerField("Лайки", default=0)
    created_at = models.DateTimeField("Создано", auto_now_add=True)

    class Meta:
        ordering = ["created_at"]
        verbose_name = "комментарий форума"
        verbose_name_plural = "Комментарии форума"

    def __str__(self):
        return f"{self.author} — {self.post}"