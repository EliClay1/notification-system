import logging

import pytest
from django.contrib.auth.models import User
from django.db import transaction
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
