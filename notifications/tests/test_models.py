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

    # Create 5 additional notifications specificially for user0
    user0 = User.objects.get(username="user0")
    for i in range(5):
        notification = NotificationModel.objects.create(
            recipient=user0, type="1", message=f"Test message to: {user0}"
        )

        NotificationModel.objects.filter(pk=notification.pk).update(
            created_at=base_time + timedelta(minutes=i + 15), is_read=i <= 10
        )

        created_ids.append(notification.pk)

    return created_ids


@pytest.fixture
def notifications_100():
    """Creates 10 notifications per user for 10 users."""
    base_time = timezone.now()
    created_ids = []
    users = []

    for i in range(10):
        user = User.objects.create_user(username=f"user{i}")
        users.append(user)

    for i in range(100):
        id = i % 10
        notification = NotificationModel.objects.create(
            recipient=users[id], type="1", message=f"Test message to: {users[id]}"
        )

        NotificationModel.objects.filter(pk=notification.pk).update(
            created_at=base_time + timedelta(minutes=id), is_read=id <= 5
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

        assert NotificationModel.objects.filter(recipient=user0).count() == 6
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
        ) == [user.pk for _i in range(6)]

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


@pytest.mark.django_db
class TestDatabaseOptimizations:
    def test_no_relation_optimization(
        self, notifications_100, django_assert_num_queries
    ):
        with django_assert_num_queries(101):
            notifications = NotificationModel.objects.all()
            for notification in notifications:
                print(notification.recipient.username)

    def test_select_related(self, notifications_100, django_assert_num_queries):
        with django_assert_num_queries(1):
            notifications = NotificationModel.objects.select_related("recipient")
            for notification in notifications:
                print(notification.recipient.username)

    def test_prefetch_related(self, notifications_100, django_assert_num_queries):
        with django_assert_num_queries(2):
            notifications = NotificationModel.objects.prefetch_related("recipient")
            for notification in notifications:
                print(notification.recipient.username)

    def test_same_return_data(self, notifications_100):
        unoptimized = list(NotificationModel.objects.order_by("pk"))
        optimized = list(
            NotificationModel.objects.select_related("recipient").order_by("pk")
        )

        assert unoptimized == optimized

        unoptimized_data = [
            (n.pk, n.message, n.recipient.username) for n in unoptimized
        ]
        optimized_data = [(n.pk, n.message, n.recipient.username) for n in optimized]

        assert unoptimized_data == optimized_data


@pytest.mark.django_db
class TestIndexes:
    def test_explain(self, notifications_100):
        notifications = NotificationModel.objects.select_related("recipient")
        logger.info(notifications.sql_execution())

        user = User.objects.get(username="user8")
        logger.info(
            NotificationModel.objects.for_user(user).unread().recent().sql_execution()
        )
