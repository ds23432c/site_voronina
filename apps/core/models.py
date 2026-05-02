from django.conf import settings
from django.db import models
from django.utils.text import slugify


class ArticleCategory(models.TextChoices):
    TAXES = "taxes", "Налоги"
    REPORTING = "reporting", "Отчетность"
    DOCUMENTS = "documents", "Первичные документы"
    PAYROLL = "payroll", "Зарплата"
    AUDIT = "audit", "Проверки"
    DIGITAL = "digital", "Цифровизация"


class Calculation(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="calculations",
        verbose_name="пользователь",
    )
    title = models.CharField("название", max_length=255)
    calculation_type = models.CharField("тип расчёта", max_length=100, blank=True)
    inputs = models.JSONField("входные данные", default=dict, blank=True)
    result = models.JSONField("результат", default=dict, blank=True)
    notes = models.TextField("примечание", blank=True)
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    class Meta:
        verbose_name = "расчёт"
        verbose_name_plural = "расчёты"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class Article(models.Model):
    title = models.CharField("заголовок", max_length=255)
    slug = models.SlugField("slug", max_length=255, unique=True)
    content = models.TextField("содержимое")
    category = models.CharField(
        "категория",
        max_length=32,
        choices=ArticleCategory.choices,
    )
    cover_url = models.URLField("обложка", max_length=500)
    is_published = models.BooleanField("опубликовано", default=True)
    created_at = models.DateTimeField("создано", auto_now_add=True)
    views_count = models.PositiveIntegerField("просмотры", default=0)

    class Meta:
        verbose_name = "статья"
        verbose_name_plural = "статьи"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)