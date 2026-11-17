import logging

import pytest
from django.contrib.auth.models import User

from notifications import services
from notifications.models import NotificationModel

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestServices:
    def test_create_notification(self):
        user = User.objects.create(username="user0")
        notification = services.create_notification(
            user, "Welcome to your account, user0!"
        )

        assert isinstance(notification, NotificationModel)

        retrieved_notification = NotificationModel.objects.get(pk=notification.pk)
        assert retrieved_notification.recipient == user
        assert retrieved_notification.message == "Welcome to your account, user0!"
        assert retrieved_notification.type == "1"

        notification2 = services.create_notification(
            user, "Welcome to your account, user0!", "2"
        )
        retrieved_notification2 = NotificationModel.objects.get(pk=notification2.pk)

        assert retrieved_notification2.type == "2"
