from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

NOTIFICATION_TYPE_CHOICES = [
    ("1", "Normal"),
    ("2", "Warning"),
    ("3", "Critical"),
]


class NotificationModel(models.Model):
    class Meta:
        ordering = ["created_at"]  # noqa: RUF012

    recipient = models.ForeignKey(User, on_delete=models.CASCADE, null=False)
    type = models.CharField(choices=NOTIFICATION_TYPE_CHOICES, default="1")
    message = models.CharField(max_length=500)
    created_at = models.DateField(default=timezone.now)
    is_read = models.BooleanField(default=False)
