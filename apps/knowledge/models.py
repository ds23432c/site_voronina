from django.db import models
from django.urls import reverse
from django.utils.text import slugify


class KnowledgeArticle(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    slug = models.SlugField("Slug", max_length=280, unique=True, blank=True)
    excerpt = models.CharField("Краткое описание", max_length=360)
    content = models.TextField("Текст статьи")
    cover_url = models.URLField("Обложка", max_length=500, blank=True)
    views_count = models.PositiveIntegerField("Просмотры", default=0)
    is_featured = models.BooleanField("Рекомендуемая", default=False)
    is_published = models.BooleanField("Опубликовано", default=True)
    published_at = models.DateTimeField("Дата публикации", auto_now_add=True)
    created_at = models.DateTimeField("Создано", auto_now_add=True)
    updated_at = models.DateTimeField("Обновлено", auto_now=True)

    class Meta:
        ordering = ["-published_at", "-created_at"]
        verbose_name = "статья базы знаний"
        verbose_name_plural = "Статьи базы знаний"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or "article"
            slug = base_slug
            index = 1
            while KnowledgeArticle.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                index += 1
                slug = f"{base_slug}-{index}"
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("knowledge:detail", kwargs={"slug": self.slug})

    def __str__(self):
        return self.title