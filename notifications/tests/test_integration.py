import logging

import pytest
from django.contrib.auth.models import User
from django.db import transaction
from django.test import Client, TestCase
from pytest_mock import MockType

from notifications.models import NotificationModel
from notifications.services import create_notification

logger = logging.getLogger(__name__)


@pytest.mark.keep_user_signal
@pytest.mark.django_db(transaction=True)
class TestIntegration:
    def test_successful_user_creation(self, mocker):
        mock_publish: MockType = mocker.patch(
            "notifications.services.publish_notification"
        )
        with transaction.atomic():
            user = User.objects.create(username="user0")

            assert NotificationModel.objects.filter(recipient=user).exists()
            mock_publish.assert_not_called()

        mock_publish.assert_called_once()

    def test_failed_user_creation(self, mocker):
        mock_publish: MockType = mocker.patch(
            "notifications.services.publish_notification"
        )
        try:
            with transaction.atomic():
                user = User.objects.create(username="user0")
                raise RuntimeError("Failed to create user.")
        except RuntimeError:
            pass

        mock_publish.assert_not_called()
        assert not NotificationModel.objects.filter(recipient=user).exists()

    @pytest.mark.disable_user_signal
    def test_multi_notification_creation(self, mocker):
        user = User.objects.create(username="user0")

        mock_publish: MockType = mocker.patch(
            "notifications.services.publish_notification"
        )

        with transaction.atomic():
            create_notification(user, "test message 1.")
            create_notification(user, "test message 2.")
            create_notification(user, "test message 3.")
            mock_publish.assert_not_called()

        assert NotificationModel.objects.filter(recipient=user).count() == 3
        assert mock_publish.call_count == 3


class TestIntegrationAPI(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(username="user1", password="password")
        self.user2 = User.objects.create(username="user2", password="password")

        self.notification1 = create_notification(recipient=self.user1, message="user1")
        self.notification2 = create_notification(recipient=self.user2, message="user2")

    def read_and_update_notification(self, user: User, notification: NotificationModel):
        self.client.force_login(user)
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, user.username)

        response = self.client.get("/api/notifications/unread/count")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 1)

        response = self.client.post(f"/api/notifications/{notification.pk}/read")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/api/notifications/unread/count")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["count"], 0)

    def test_isolation_and_notification_lifecycle(self):
        self.read_and_update_notification(self.user1, self.notification1)
        self.read_and_update_notification(self.user2, self.notification2)

    def test_csrf_enforcement(self):
        self.client = Client(enforce_csrf_checks=True)
        self.client.force_login(self.user1)
        response = self.client.post(f"/api/notifications/{self.notification1.pk}/read")
        self.assertEqual(response.status_code, 403)
