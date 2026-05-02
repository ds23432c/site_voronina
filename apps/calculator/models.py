from django.conf import settings
from django.db import models


class Calculation(models.Model):
    class CalculationType(models.TextChoices):
        NDFL = "ndfl", "НДФЛ"
        CONTRIBUTIONS = "contributions", "Страховые взносы"
        USN = "usn", "УСН"
        VAT = "vat", "НДС"
        PENI = "peni", "Пени"
        SALARY = "salary", "Зарплата"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="calculator_calculations",
        verbose_name="Пользователь",
    )
    calculation_type = models.CharField(
        max_length=32,
        choices=CalculationType.choices,
        verbose_name="Тип расчета",
    )
    input_data = models.JSONField(default=dict, verbose_name="Исходные данные")
    result_data = models.JSONField(default=dict, verbose_name="Результат")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        ordering = ("-created_at",)
        verbose_name = "Расчет"
        verbose_name_plural = "Расчеты"

    def __str__(self) -> str:
        return f"{self.get_calculation_type_display()} #{self.pk}"
