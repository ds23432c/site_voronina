from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="TaxDeadline",
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
                ("title", models.CharField(max_length=255, verbose_name="Название")),
                ("deadline_date", models.DateField(verbose_name="Срок")),
                (
                    "org_type",
                    models.CharField(
                        choices=[
                            ("all", "Все"),
                            ("ooo", "ООО"),
                            ("ip", "ИП"),
                        ],
                        default="all",
                        max_length=8,
                        verbose_name="Тип организации",
                    ),
                ),
                (
                    "tax_system",
                    models.CharField(
                        choices=[
                            ("all", "Все"),
                            ("osn", "ОСН"),
                            ("usn", "УСН"),
                            ("psn", "ПСН"),
                        ],
                        default="all",
                        max_length=8,
                        verbose_name="Система налогообложения",
                    ),
                ),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
            ],
            options={
                "verbose_name": "Налоговый срок",
                "verbose_name_plural": "Налоговые сроки",
                "ordering": ("deadline_date", "title"),
            },
        ),
    ]