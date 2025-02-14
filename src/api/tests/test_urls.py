from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class TestUrls(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
        )

    def test_positive_login_url(self):
        url = reverse("api:token_obtain_pair")
        payload = {
            "username": "testuser",
            "password": "testpassword",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)

    def test_negative_login_url(self):
        url = reverse("api:token_obtain_pair")
        payload = {
            "username": "testuser",
            "password": "wrongpassword",
        }
        response = self.client.post(url, payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_refresh_token_url(self):
        login_url = reverse("api:token_obtain_pair")
        login_payload = {
            "username": "testuser",
            "password": "testpassword",
        }
        login_response = self.client.post(login_url, login_payload, format="json")
        refresh_token = login_response.data.get("refresh")
        refresh_url = reverse("api:token_refresh")
        response = self.client.post(refresh_url, {"refresh": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)

    def test_logout_url(self):
        login_url = reverse("api:token_obtain_pair")
        login_payload = {
            "username": "testuser",
            "password": "testpassword",
        }
        login_response = self.client.post(login_url, login_payload, format="json")
        refresh_token = login_response.data.get("refresh")

        logout_url = reverse("api:token_blacklist")
        response = self.client.post(logout_url, {"refresh": refresh_token}, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        refresh_url = reverse("api:token_refresh")
        refresh_response = self.client.post(refresh_url, {"refresh": refresh_token}, format="json")
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
