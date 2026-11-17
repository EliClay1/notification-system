import logging

import pytest
from django.contrib.auth.models import User

from notifications.models import NotificationModel

logger = logging.getLogger(__name__)


@pytest.mark.keep_user_signal
@pytest.mark.django_db
class TestNotificationSignals:
    def test_user_creation_signal(self):
        user = User.objects.create(username="user0")
        # by this point, the signal should have activated.

        # check if the notification actually got created.
        notifications = NotificationModel.objects.filter(recipient=user)

        assert notifications.count() == 1

    def test_update_existing_user(self):
        user = User.objects.create(username="user0")
        user.set_password("password123")
        user.save()

        notifications = NotificationModel.objects.filter(recipient=user)
        assert notifications.count() == 1
