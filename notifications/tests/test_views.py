import logging

import pytest
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.test import Client, TestCase

from notifications.middleware import Middleware
from notifications.services import create_notification

logger = logging.getLogger(__name__)


@pytest.mark.django_db
class TestGetNotifications(TestCase):
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


@pytest.mark.django_db
class TestReadNotifications(TestCase):
    def setUp(self):
        self.client = Client()
        self.user1 = User.objects.create(username="user1", password="password")
        self.user2 = User.objects.create(username="user2", password="password")
        self.notification1 = create_notification(recipient=self.user1, message="user1")
        self.notification2 = create_notification(recipient=self.user2, message="user2")

    def test_read_own_notification(self):
        self.client.force_login(self.user1)
        response = self.client.post(f"/api/notifications/{self.notification1.pk}/read")
        self.assertEqual(response.status_code, 200)
        self.notification1.refresh_from_db()
        self.assertTrue(self.notification1.is_read)

    def test_read_others_notification(self):
        self.client.force_login(self.user1)
        response = self.client.post(f"/api/notifications/{self.notification2.pk}/read")
        self.assertEqual(response.status_code, 404)
        self.notification2.refresh_from_db()
        self.assertFalse(self.notification2.is_read)

    def test_unauth_read_notification(self):
        response = self.client.post(f"/api/notifications/{self.notification1.pk}/read")
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f"/login/?next=/api/notifications/{self.notification1.pk}/read",
            fetch_redirect_response=False,
        )

        login_response = self.client.get("/login/")
        self.assertTemplateUsed(login_response, "registration/login.html")

    def test_get_read_notification(self):
        self.client.force_login(self.user1)
        response = self.client.get(f"/api/notifications/{self.notification1.pk}/read")
        self.assertEqual(response.status_code, 405)


@pytest.mark.django_db
class TestMiddleware(TestCase):
    def setUp(self):
        self.client = Client(raise_request_exception=False)
        self.user1 = User.objects.create(username="user1", password="password")
        self.notification1 = create_notification(recipient=self.user1, message="user1")

    def test_good_request(self):
        self.client.force_login(self.user1)
        with self.assertLogs("notifications.middleware", level="INFO") as logs:
            response = self.client.get("/api/notifications/")

            self.assertEqual(response.status_code, 200)
            self.assertIn("[GET] '/api/notifications/", logs.output[0])
            self.assertIn("Status: 200", logs.output[0])

    def test_missing_endpoint(self):
        self.client.force_login(self.user1)
        with self.assertLogs("notifications.middleware", level="INFO") as logs:
            response = self.client.post(
                f"/api/notifications/{self.notification1.pk}/rea"
            )

            self.assertEqual(response.status_code, 404)
            self.assertIn("[POST] '/api/notifications/", logs.output[0])
            self.assertIn("Status: 404", logs.output[0])

    def test_exception(self):
        self.client.force_login(self.user1)
        request = HttpRequest()
        request.method = "GET"
        request.path = "/test-error/"

        middleware = Middleware(lambda request: HttpResponse(status=500))

        with self.assertLogs("notifications.middleware", level="INFO") as logs:
            response = middleware(request)
            self.assertEqual(response.status_code, 500)
            self.assertIn("Status: 500", logs.output[0])
