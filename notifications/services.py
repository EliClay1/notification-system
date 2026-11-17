import logging

from django.contrib.auth.models import User
from django.db import transaction

from notifications.models import NotificationModel

logger = logging.getLogger(__name__)


def create_notification(recipient: User, message: str, notification_type="1"):

    notification = NotificationModel.objects.create(
        recipient=recipient,
        message=message,
        type=notification_type,
    )
    if notification is None:
        return

    transaction.on_commit(lambda: publish_notification(notification))
    return notification


def publish_notification(notification):
    logger.info(
        f"notification to {notification.recipient.username} has been published "
        "and sent through the websocket."
    )
