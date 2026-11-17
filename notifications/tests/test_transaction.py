import logging

import pytest
from django.contrib.auth.models import User
from django.db import transaction
from pytest_mock import MockType

from notifications.models import NotificationModel
from notifications.services import create_notification

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestTransactions:
    def test_successful_transaction(self):
        user = User.objects.create(username="user0")
        with transaction.atomic():
            create_notification(recipient=user, message="test message 1")
            create_notification(recipient=user, message="test message 2")
        count = NotificationModel.objects.filter(recipient=user).count()
        assert count == 2

    def test_failed_transaction(self):
        user = User.objects.create(username="user0")
        try:
            with transaction.atomic():
                create_notification(recipient=user, message="test message 1")
                create_notification(recipient=user, message="test message 2")
                raise RuntimeError("Transaction failed")
        except RuntimeError:
            pass

        assert not NotificationModel.objects.filter(recipient=user).exists()


@pytest.mark.django_db(transaction=True)
class TestCommitTransactions:
    def test_successful_commit_transaction(self, mocker):
        mock_publish: MockType = mocker.patch(
            "notifications.services.publish_notification"
        )

        user = User.objects.create(username="user0")
        with transaction.atomic():
            create_notification(recipient=user, message="test message 1")
            mock_publish.assert_not_called()

        mock_publish.assert_called_once()

    def test_failed_commit_transaction(self, mocker):
        mock_publish: MockType = mocker.patch(
            "notifications.services.publish_notification"
        )

        user = User.objects.create(username="user0")
        try:
            with transaction.atomic():
                create_notification(recipient=user, message="test message 1")
                raise RuntimeError("Transaction failed")
        except RuntimeError:
            pass

        mock_publish.assert_not_called()

    def test_immediate_commit(self, mocker):
        mock_publish: MockType = mocker.patch(
            "notifications.services.publish_notification"
        )

        user = User.objects.create(username="user0")
        create_notification(recipient=user, message="test message 1")

        mock_publish.assert_called_once()
