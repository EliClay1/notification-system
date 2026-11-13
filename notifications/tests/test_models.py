import logging
from datetime import datetime, timedelta
from unittest import TestCase

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

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
                recipient=new_user, type="1", message=f"message #{i}"
            )

        new_user2 = User.objects.create_user(username="user2")
        NotificationModel.objects.create(recipient=new_user2, type="1", message="test")

        # base assumptions, and checks if the notification is connected to the right user.
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
        base_time = timezone.now()

        notifications = [
            ("user1", base_time),
            ("user2", base_time + timedelta(minutes=1)),
            ("user3", base_time + timedelta(minutes=2)),
        ]

        expected_ids = []

        for username, created_at in notifications:
            user = User.objects.create_user(username=username)
            notification = NotificationModel.objects.create(
                recipient=user, type="1", message=f"test message to {username}"
            )
            NotificationModel.objects.filter(pk=notification.pk).update(
                created_at=created_at
            )

            expected_ids.insert(0, notification.pk)

        actual_ids = list(NotificationModel.objects.values_list("pk", flat=True))

        self.assertEqual(actual_ids, expected_ids)
