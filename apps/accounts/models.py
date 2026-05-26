from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


class UserRole(models.TextChoices):
    OWNER = "owner", "Владелец бизнеса"
    ACCOUNTANT = "accountant", "Бухгалтер"
    MANAGER = "manager", "Менеджер"
    CONSULTANT = "consultant", "Консультант"


class OrganizationType(models.TextChoices):
    IP = "ip", "ИП"
    OOO = "ooo", "ООО"
    SELF_EMPLOYED = "self_employed", "Самозанятый"
    NONPROFIT = "nonprofit", "НКО"


class TaxSystem(models.TextChoices):
    OSNO = "osno", "ОСНО"
    USN_6 = "usn_6", "УСН 6%"
    USN_15 = "usn_15", "УСН 15%"
    PATENT = "patent", "Патент"
    NPD = "npd", "НПД"


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Пользователь должен иметь email")
        email = self.normalize_email(email).lower()
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("role", UserRole.OWNER)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("role", UserRole.OWNER)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Суперпользователь должен иметь is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Суперпользователь должен иметь is_superuser=True.")
        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField("электронная почта", unique=True)
    role = models.CharField("роль", max_length=32, choices=UserRole.choices, default=UserRole.OWNER)
    organization_type = models.CharField(
        "тип организации",
        max_length=32,
        choices=OrganizationType.choices,
        default=OrganizationType.IP,
    )
    tax_system = models.CharField(
        "налоговая система",
        max_length=32,
        choices=TaxSystem.choices,
        default=TaxSystem.USN_6,
    )
    phone = models.CharField("телефон", max_length=20, blank=True)
    avatar = models.URLField("аватар", blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "пользователь"
        verbose_name_plural = "пользователи"

    def __str__(self):
        return self.get_full_name() or self.email

    @property
    def display_name(self):
        return self.get_full_name() or self.email


class Organization(models.Model):
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organizations",
        verbose_name="владелец",
    )
    name = models.CharField("название", max_length=255)
    organization_type = models.CharField(
        "тип организации",
        max_length=32,
        choices=OrganizationType.choices,
        default=OrganizationType.IP,
    )
    tax_system = models.CharField(
        "налоговая система",
        max_length=32,
        choices=TaxSystem.choices,
        default=TaxSystem.USN_6,
    )
    inn = models.CharField("ИНН", max_length=12)
    kpp = models.CharField("КПП", max_length=9, blank=True)
    phone = models.CharField("телефон", max_length=20, blank=True)
    email = models.EmailField("рабочая почта", blank=True)
    address = models.CharField("адрес", max_length=255, blank=True)
    website = models.URLField("сайт", blank=True)
    description = models.TextField("описание", blank=True)
    created_at = models.DateTimeField("создано", auto_now_add=True)
    updated_at = models.DateTimeField("обновлено", auto_now=True)

    class Meta:
        verbose_name = "организация"
        verbose_name_plural = "организации"
        ordering = ["name"]

    def __str__(self):
        return self.name
