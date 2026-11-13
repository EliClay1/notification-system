import logging
from datetime import datetime

import pytest
from django.contrib.auth.models import User
from django.test import TestCase

from notifications.models import NotificationModel

logger = logging.getLogger(__name__)


class NotificationModelTests(TestCase):
    """
    Tests the various function of the notification model.
    """

    @pytest.mark.django_db
    def test_notification_creation(self):

        # Arrange
        user1 = User.objects.create_user(username="test1")
        notification = NotificationModel(
            recipient=user1, type="1", message="This is a test message"
        )

        # Act
        notification.save()
        saved_notification = NotificationModel.objects.get(pk=notification.pk)

        # Assert
        self.assertEqual(notification, saved_notification)
        self.assertFalse(notification.is_read)
        self.assertIsInstance(notification.created_at, datetime)

    @pytest.mark.django_db
    def test_notification_relationships(self):
        new_user = User.objects.create_user(username="user1")

        for i in range(10):
            NotificationModel.objects.create(
                recipient=new_user, type=type, message=f"message #{i}"
            )

        new_user2 = User.objects.create_user(username="user2")
        NotificationModel.objects.create(recipient=new_user2, type=type, message="test")

        # base assumptions
        self.assertEqual(
            NotificationModel.objects.filter(recipient=new_user).count(), 10
        )
        self.assertEqual(
            NotificationModel.objects.filter(recipient=new_user2).count(), 1
        )

        # Cascade check
        user_id = new_user.pk
        new_user.delete()
        self.assertFalse(
            NotificationModel.objects.filter(recipient_id=user_id).exists()
        )
        self.assertEqual(
            NotificationModel.objects.filter(recipient=new_user2).count(), 1
        )

    @pytest.mark.django_db
    def test_notification_order(self):

        notifications = {
            "user2": {"type": "1", "message": "test message to user2"},
            "user1": {"type": "1", "message": "test message to user1"},
            "user3": {"type": "1", "message": "test message to user3"},
            "user4": {"type": "1", "message": "test message to user4"},
            "user5": {"type": "1", "message": "test message to user5"},
        }

        for user, data in notifications.items():
            type = data["type"]
            message = data["message"]

            new_user = User.objects.create_user(username=user)
            notification = NotificationModel(
                recipient=new_user, type=type, message=message
            )
            notification.save()

        self.assertEqual(
            list(NotificationModel.objects.values_list("pk", flat=True)),
            list(
                NotificationModel.objects.order_by("created_at").values_list(
                    "pk", flat=True
                )
            ),
        )
