import apps.accounts.models as accounts_models
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(blank=True, null=True, verbose_name="last login"),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
                ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
                ("is_staff", models.BooleanField(default=False, verbose_name="staff status")),
                ("is_active", models.BooleanField(default=True, verbose_name="active")),
                (
                    "date_joined",
                    models.DateTimeField(default=timezone.now, verbose_name="date joined"),
                ),
                ("email", models.EmailField(max_length=254, unique=True, verbose_name="электронная почта")),
                (
                    "role",
                    models.CharField(
                        choices=accounts_models.UserRole.choices,
                        default=accounts_models.UserRole.OWNER,
                        max_length=32,
                        verbose_name="роль",
                    ),
                ),
                (
                    "organization_type",
                    models.CharField(
                        choices=accounts_models.OrganizationType.choices,
                        default=accounts_models.OrganizationType.IP,
                        max_length=32,
                        verbose_name="тип организации",
                    ),
                ),
                (
                    "tax_system",
                    models.CharField(
                        choices=accounts_models.TaxSystem.choices,
                        default=accounts_models.TaxSystem.USN_6,
                        max_length=32,
                        verbose_name="налоговая система",
                    ),
                ),
                ("phone", models.CharField(blank=True, max_length=20, verbose_name="телефон")),
                (
                    "avatar",
                    models.ImageField(blank=True, null=True, upload_to="avatars/", verbose_name="аватар"),
                ),
                (
                    "groups",
                    models.ManyToManyField(
                        blank=True,
                        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.group",
                        verbose_name="groups",
                    ),
                ),
                (
                    "user_permissions",
                    models.ManyToManyField(
                        blank=True,
                        help_text="Specific permissions for this user.",
                        related_name="user_set",
                        related_query_name="user",
                        to="auth.permission",
                        verbose_name="user permissions",
                    ),
                ),
            ],
            options={
                "verbose_name": "пользователь",
                "verbose_name_plural": "пользователи",
            },
            managers=[
                ("objects", accounts_models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name="Organization",
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
                ("name", models.CharField(max_length=255, verbose_name="название")),
                (
                    "organization_type",
                    models.CharField(
                        choices=accounts_models.OrganizationType.choices,
                        default=accounts_models.OrganizationType.IP,
                        max_length=32,
                        verbose_name="тип организации",
                    ),
                ),
                (
                    "tax_system",
                    models.CharField(
                        choices=accounts_models.TaxSystem.choices,
                        default=accounts_models.TaxSystem.USN_6,
                        max_length=32,
                        verbose_name="налоговая система",
                    ),
                ),
                ("inn", models.CharField(max_length=12, verbose_name="ИНН")),
                ("kpp", models.CharField(blank=True, max_length=9, verbose_name="КПП")),
                ("phone", models.CharField(blank=True, max_length=20, verbose_name="телефон")),
                ("email", models.EmailField(blank=True, max_length=254, verbose_name="рабочая почта")),
                ("address", models.CharField(blank=True, max_length=255, verbose_name="адрес")),
                ("website", models.URLField(blank=True, verbose_name="сайт")),
                ("description", models.TextField(blank=True, verbose_name="описание")),
                (
                    "created_at",
                    models.DateTimeField(auto_now_add=True, verbose_name="создано"),
                ),
                (
                    "updated_at",
                    models.DateTimeField(auto_now=True, verbose_name="обновлено"),
                ),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="organizations",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="владелец",
                    ),
                ),
            ],
            options={
                "verbose_name": "организация",
                "verbose_name_plural": "организации",
                "ordering": ["name"],
            },
        ),
    ]