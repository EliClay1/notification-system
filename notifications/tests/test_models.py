import pytest
from django.contrib.auth.models import User
from django.test import TestCase

from ..models import NotificationModel


class NotificationModelTests(TestCase):
    """
    Tests the various function of the notification model.
    """

    @pytest.mark.django_db
    def test_notification_creation(self):

        # Arrange
        me = User.objects.get(username="eliclay1")
        notification = NotificationModel(receipient=me, type="1")

        # Act
        notification.save()

        # Assert
