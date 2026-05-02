from decimal import Decimal

from django.conf import settings
from django.db import models


class SafeDict(dict):
    def __missing__(self, key):
        return ""


def _format_value(value):
    if value is None:
        return ""
    if hasattr(value, "strftime"):
        return value.strftime("%d.%m.%Y")
    if isinstance(value, Decimal):
        text = f"{value:,.2f}".replace(",", " ").replace(".", ",")
        return text
    return str(value)


class DocumentTemplate(models.Model):
    slug = models.SlugField(max_length=80, unique=True, verbose_name="Код шаблона")
    title = models.CharField(max_length=200, verbose_name="Название")
    description = models.TextField(blank=True, verbose_name="Описание")
    template_text = models.TextField(verbose_name="Текст шаблона")

    class Meta:
        ordering = ("title",)
        verbose_name = "Шаблон документа"
        verbose_name_plural = "Шаблоны документов"

    def __str__(self) -> str:
        return self.title

    def render(self, data: dict) -> str:
        normalized = {key: _format_value(value) for key, value in data.items()}
        return self.template_text.format_map(SafeDict(normalized))


class GeneratedDocument(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="generated_documents",
        verbose_name="Пользователь",
    )
    template = models.ForeignKey(
        DocumentTemplate,
        on_delete=models.PROTECT,
        related_name="generated_documents",
        verbose_name="Шаблон",
    )
    input_data = models.JSONField(default=dict, verbose_name="Исходные данные")
    rendered_text = models.TextField(verbose_name="Сгенерированный текст")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Сгенерированный документ"
        verbose_name_plural = "Сгенерированные документы"

    def __str__(self) -> str:
        return f"{self.template.title} #{self.pk}"

    @property
    def filename(self) -> str:
        return f"{self.template.slug}.txt"