from typing import cast

from django.conf import settings
from django.db import models


class NotificationQuerySet(models.QuerySet):
    def unread(self):
        """Returns any unread notifications"""
        return self.filter(is_read=False)

    def for_user(self, user):
        """Returns all notifications for the user"""
        return self.filter(recipient=user)

    def recent(self):
        """Returns the 10 most recent notifications"""
        # order_by is not required here, as it automatically returns by the 10 most recent.
        return self.order_by("-created_at", "-pk")[:10]


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

    # Cast for type checking in functions.
    objects = cast(NotificationQuerySet, NotificationQuerySet.as_manager())

    class Meta:
        ordering = ["-created_at"]  # noqa: RUF012

    def __str__(self) -> str:
        return f"{self.recipient.username}: {self.message}"
