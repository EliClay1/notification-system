from django.conf import settings
from django.db import models


class NotificationModel(models.Model):
    class NotificationType(models.TextChoices):
        NORMAL = ("1", "Normal")
        IMPORTANT = ("2", "Important")
        CRITICAL = ("3", "Critical")

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications"
    )
    type = models.CharField(
        choices=NotificationType.choices, default=NotificationType.NORMAL
    )
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]  # noqa: RUF012

    def __str__(self) -> str:
        return f"{self.recipient.username}: {self.message}"
