from datetime import timedelta

from django.db import models
from django.utils import timezone


class OrganizationType(models.TextChoices):
    ALL = "all", "Все"
    LLC = "ooo", "ООО"
    IP = "ip", "ИП"


class TaxSystem(models.TextChoices):
    ALL = "all", "Все"
    OSN = "osn", "ОСН"
    USN = "usn", "УСН"
    PSN = "psn", "ПСН"


class TaxDeadline(models.Model):
    title = models.CharField(max_length=255, verbose_name="Название")
    deadline_date = models.DateField(verbose_name="Срок")
    org_type = models.CharField(max_length=8, choices=OrganizationType.choices, default=OrganizationType.ALL, verbose_name="Тип организации")
    tax_system = models.CharField(max_length=8, choices=TaxSystem.choices, default=TaxSystem.ALL, verbose_name="Система налогообложения")
    description = models.TextField(blank=True, verbose_name="Описание")

    class Meta:
        ordering = ("deadline_date", "title")
        verbose_name = "Налоговый срок"
        verbose_name_plural = "Налоговые сроки"

    def __str__(self) -> str:
        return f"{self.deadline_date:%d.%m.%Y} — {self.title}"

    @property
    def is_urgent(self) -> bool:
        today = timezone.localdate()
        return today <= self.deadline_date <= today + timedelta(days=14)

    @property
    def days_left(self) -> int:
        return (self.deadline_date - timezone.localdate()).days