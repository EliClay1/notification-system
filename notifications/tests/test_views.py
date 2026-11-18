import logging

import pytest
from django.contrib.auth.models import User
from django.test import Client, TestCase

from notifications.services import create_notification

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestViews(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(username="user1", password="password")
        self.user2 = User.objects.create(username="user2", password="password")

        create_notification(recipient=self.user1, message="user1")
        create_notification(recipient=self.user2, message="user2")

    def test_authenticated_user_notifications(self):
        self.client.force_login(self.user1)
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "user1")

    def test_notification_isolation(self):
        self.client.force_login(self.user1)
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "user2")

    def test_anonymous_access(self):
        response = self.client.get("/api/notifications/")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            "/login/?next=/api/notifications/",
            fetch_redirect_response=False,
        )

        login_response = self.client.get("/login/")
        self.assertTemplateUsed(login_response, "registration/login.html")
