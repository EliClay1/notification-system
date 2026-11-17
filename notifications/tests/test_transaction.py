import logging

import pytest
from django.contrib.auth.models import User
from django.db import transaction

from notifications.models import NotificationModel

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestTransactions:
    def test_successful_transaction(self):
        user = User.objects.create(username="user0")
        with transaction.atomic():
            NotificationModel.objects.create(recipient=user, message="test message 1")
            NotificationModel.objects.create(recipient=user, message="test message 2")
        count = NotificationModel.objects.filter(recipient=user).count()
        assert count == 2

    def test_failed_transaction(self):
        user = User.objects.create(username="user0")

        with pytest.raises(RuntimeError), transaction.atomic():
            NotificationModel.objects.create(recipient=user, message="test message")
            raise RuntimeError("Transaction failed")

        assert not NotificationModel.objects.filter(recipient=user).exists()
