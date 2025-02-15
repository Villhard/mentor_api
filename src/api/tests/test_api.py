from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class TestUrls(APITestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.urls = {
            "login": reverse("api:token_obtain_pair"),
            "refresh": reverse("api:token_refresh"),
            "logout": reverse("api:token_blacklist"),
        }

    def setUp(self):
        super().setUp()
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )
        response = self.client.post(
            self.urls["login"],
            {
                "username": "testuser",
                "password": "testpassword",
            },
            format="json",
        )
        self.access_token = response.data["access"]
        self.refresh_token = response.data["refresh"]

    def tearDown(self):
        super().tearDown()
        self.user.delete()

    def test_login_success(self):
        payload = {
            "username": "testuser",
            "password": "testpassword",
        }

        response = self.client.post(self.urls["login"], payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_login_failure(self):
        payload = {
            "username": "testuser",
            "password": "wrongpassword",
        }

        response = self.client.post(self.urls["login"], payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_success(self):
        payload = {
            "refresh": self.refresh_token,
        }

        response = self.client.post(self.urls["refresh"], payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertNotEqual(response.data["access"], self.access_token)

    def test_logout_success(self):
        payload = {
            "refresh": self.refresh_token,
        }

        response = self.client.post(self.urls["logout"], payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_failure_after_logout(self):
        payload = {
            "refresh": self.refresh_token,
        }
        self.client.post(self.urls["logout"], payload, format="json")

        response = self.client.post(self.urls["refresh"], payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
