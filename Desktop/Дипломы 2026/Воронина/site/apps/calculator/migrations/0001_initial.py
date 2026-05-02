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
                (
                    "calculation_type",
                    models.CharField(
                        choices=[
                            ("ndfl", "НДФЛ"),
                            ("contributions", "Страховые взносы"),
                            ("usn", "УСН"),
                            ("vat", "НДС"),
                            ("peni", "Пени"),
                            ("salary", "Зарплата"),
                        ],
                        max_length=32,
                        verbose_name="Тип расчета",
                    ),
                ),
                ("input_data", models.JSONField(default=dict, verbose_name="Исходные данные")),
                ("result_data", models.JSONField(default=dict, verbose_name="Результат")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="calculations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Расчет",
                "verbose_name_plural": "Расчеты",
                "ordering": ("-created_at",),
            },
        ),
    ]