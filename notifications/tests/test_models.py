import logging
from datetime import datetime, timedelta

import pytest
from django.contrib.auth.models import User
from django.utils import timezone

from notifications.models import NotificationModel

logger = logging.getLogger(__name__)


@pytest.fixture
def notifications():
    base_time = timezone.now()
    created_ids = []

    for i in range(15):
        user = User.objects.create_user(username=f"user{i}")
        notification = NotificationModel.objects.create(
            recipient=user, type="1", message=f"Test message to: {user}"
        )

        NotificationModel.objects.filter(pk=notification.pk).update(
            created_at=base_time + timedelta(minutes=i), is_read=i <= 10
        )

        created_ids.append(notification.pk)

    return created_ids


@pytest.mark.django_db
class TestNotificationModel:
    def test_notification_creation(self):
        user = User.objects.create_user(username="user0")
        notification = NotificationModel.objects.create(
            recipient=user, type="1", message=f"Test message to: {user}"
        )

        retrieved = NotificationModel.objects.get(pk=notification.pk)

        assert notification == retrieved
        assert not notification.is_read
        assert isinstance(notification.created_at, datetime)

    def test_notification_relationship(self, notifications):
        user0 = User.objects.get(username="user0")
        user1 = User.objects.get(username="user1")
        user0_pk = user0.pk

        assert NotificationModel.objects.filter(recipient=user0).count() == 1
        user0.delete()
        assert not NotificationModel.objects.filter(recipient_id=user0_pk).exists()
        assert NotificationModel.objects.filter(recipient=user1).count() == 1

    def test_notification_order(self, notifications):
        assert (
            list(NotificationModel.objects.all().values_list("pk", flat=True))
            == notifications[::-1]
        )


@pytest.mark.django_db
class TestNotificationQuerySet:
    def test_unread(self, notifications):
        assert NotificationModel.objects.unread().count() == 4

    def test_for_user(self, notifications):
        user = User.objects.get(username="user0")

        assert list(
            NotificationModel.objects.for_user(user).values_list(
                "recipient_id", flat=True
            )
        ) == [user.pk]

    def test_recent(self, notifications):
        assert (
            list(NotificationModel.objects.recent().values_list("pk", flat=True))
            == notifications[::-1][:10]
        )

    def test_chained_methods(self, notifications):
        user = User.objects.get(username="user0")
        user12 = User.objects.get(username="user12")

        assert NotificationModel.objects.for_user(user).unread().count() == 0
        assert NotificationModel.objects.for_user(user12).unread().count() == 1

    def test_database_calls(self, notifications, django_assert_num_queries):
        with django_assert_num_queries(0):
            unread_data = NotificationModel.objects.unread()
            all_data_sliced = NotificationModel.objects.all()[:5]

        with django_assert_num_queries(1):
            list(unread_data)

        with django_assert_num_queries(1):
            list(all_data_sliced)
