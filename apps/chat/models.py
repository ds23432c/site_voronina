import uuid

from django.conf import settings
from django.db import models


class ChatSession(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="chat_sessions",
        verbose_name="Пользователь",
    )
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, verbose_name="ID сессии")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")

    class Meta:
        ordering = ("-updated_at",)
        verbose_name = "Сессия чата"
        verbose_name_plural = "Сессии чата"

    def __str__(self) -> str:
        return str(self.session_id)


class ChatMessage(models.Model):
    class Role(models.TextChoices):
        USER = "user", "Пользователь"
        ASSISTANT = "assistant", "Ассистент"

    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name="messages", verbose_name="Сессия")
    role = models.CharField(max_length=16, choices=Role.choices, verbose_name="Роль")
    content = models.TextField(verbose_name="Сообщение")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")

    class Meta:
        ordering = ("created_at",)
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"

    def __str__(self) -> str:
        return f"{self.get_role_display()} #{self.pk}"