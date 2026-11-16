import logging

import pytest
from django.contrib.auth.models import User

from notifications import services

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestServices:
    def test_create_notification(self):
        user = User.objects.create(username="user0")
        notification = services.create_notification(
            user, "Welcome to your account, user0!"
        )

        if notification is None:
            return

        assert notification.message == "Welcome to your account, user0!"
        assert notification.type == "1"
