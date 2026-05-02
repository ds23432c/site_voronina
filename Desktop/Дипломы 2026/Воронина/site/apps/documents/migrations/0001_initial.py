from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def create_templates(apps, schema_editor):
    DocumentTemplate = apps.get_model("documents", "DocumentTemplate")
    templates = [
        {
            "slug": "dogovor-okazaniya-uslug",
            "title": "Договор оказания услуг",
            "description": "Базовый текст договора между заказчиком и исполнителем.",
            "template_text": (
                "ДОГОВОР № {document_number} ОКАЗАНИЯ УСЛУГ\n"
                "г. {city}\n"
                "{document_date}\n\n"
                "{company_name}, в лице {director_name}, действующего на основании {basis}, "
                "именуемое в дальнейшем «Заказчик», и {contractor_name}, именуемое в дальнейшем "
                "«Исполнитель», заключили настоящий договор о нижеследующем.\n\n"
                "1. Предмет договора\n"
                "Исполнитель обязуется оказать услуги: {service_name}.\n\n"
                "2. Стоимость услуг\n"
                "Стоимость услуг составляет {amount} руб.\n\n"
                "3. Подписи сторон\n"
                "Заказчик: {director_name}\n"
                "Исполнитель: {contractor_name}\n"
            ),
        },
        {
            "slug": "akt-vypolnennyh-rabot",
            "title": "Акт выполненных работ",
            "description": "Подтверждение оказанных услуг или выполненных работ.",
            "template_text": (
                "АКТ № {document_number} ВЫПОЛНЕННЫХ РАБОТ\n"
                "г. {city}\n"
                "{document_date}\n\n"
                "Мы, нижеподписавшиеся, {company_name} в лице {director_name} и {contractor_name}, "
                "составили настоящий акт о том, что услуги {service_name} выполнены в полном объеме.\n\n"
                "Сумма к оплате: {amount} руб.\n\n"
                "Претензий по объему и качеству работ стороны не имеют.\n"
            ),
        },
        {
            "slug": "spravka-o-dohodah",
            "title": "Справка о доходах",
            "description": "Справка для сотрудника или контрагента с указанием начислений.",
            "template_text": (
                "СПРАВКА О ДОХОДАХ\n"
                "{company_name}\n"
                "{document_date}\n\n"
                "Настоящая справка выдана {employee_name}.\n"
                "Доход за указанный период составил {amount} руб.\n"
                "Основание выдачи справки: {basis}.\n\n"
                "Подпись: {director_name}\n"
            ),
        },
        {
            "slug": "pismo-o-predostavlenii-dokumentov",
            "title": "Письмо о предоставлении документов",
            "description": "Официальный запрос документов или разъяснений.",
            "template_text": (
                "ПИСЬМО\n"
                "№ {document_number} от {document_date}\n"
                "г. {city}\n\n"
                "Кому: {recipient_name}\n\n"
                "{company_name} просит предоставить документы по вопросу: {comment}.\n"
                "При необходимости ответить на запрос просим связаться с {director_name}.\n\n"
                "С уважением,\n"
                "{director_name}\n"
                "{position}\n"
            ),
        },
        {
            "slug": "prikaz-o-naznachenii",
            "title": "Приказ о назначении",
            "description": "Внутренний приказ о назначении сотрудника на должность.",
            "template_text": (
                "ПРИКАЗ № {document_number}\n"
                "о назначении\n"
                "{document_date}\n\n"
                "Назначить {employee_name} на должность {position} в {company_name}.\n"
                "Основание: {basis}.\n"
                "Комментарий: {comment}.\n\n"
                "Подпись: {director_name}\n"
            ),
        },
    ]
    DocumentTemplate.objects.bulk_create([DocumentTemplate(**item) for item in templates])


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="DocumentTemplate",
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
                ("slug", models.SlugField(max_length=80, unique=True, verbose_name="Код шаблона")),
                ("title", models.CharField(max_length=200, verbose_name="Название")),
                ("description", models.TextField(blank=True, verbose_name="Описание")),
                ("template_text", models.TextField(verbose_name="Текст шаблона")),
            ],
            options={
                "verbose_name": "Шаблон документа",
                "verbose_name_plural": "Шаблоны документов",
                "ordering": ("title",),
            },
        ),
        migrations.CreateModel(
            name="GeneratedDocument",
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
                ("input_data", models.JSONField(default=dict, verbose_name="Исходные данные")),
                ("rendered_text", models.TextField(verbose_name="Сгенерированный текст")),
                ("created_at", models.DateTimeField(auto_now_add=True, verbose_name="Создано")),
                (
                    "template",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="generated_documents",
                        to="documents.documenttemplate",
                        verbose_name="Шаблон",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="generated_documents",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="Пользователь",
                    ),
                ),
            ],
            options={
                "verbose_name": "Сгенерированный документ",
                "verbose_name_plural": "Сгенерированные документы",
                "ordering": ("-created_at",),
            },
        ),
        migrations.RunPython(create_templates, migrations.RunPython.noop),
    ]