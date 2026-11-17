from django.contrib.auth.models import User

from notifications.models import NotificationModel


def create_notification(recipient: User, message: str, notification_type="1"):
    notification = NotificationModel.objects.create(
        recipient=recipient,
        message=message,
        type=notification_type,
    )
    return notification
