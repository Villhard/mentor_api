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
            "registration": reverse("api:registration"),
            "login": reverse("api:token_obtain_pair"),
            "refresh": reverse("api:token_refresh"),
            "logout": reverse("api:token_blacklist"),
            "users": reverse("api:users-list"),
            "user_detail": lambda user_id: reverse("api:users-detail", args=[user_id]),
        }

        cls.user_no_relations = User.objects.create_user(
            username="no_relations",
            password="testpass123"
        )
        cls.user_with_mentees = User.objects.create_user(
            username="has_mentees",
            password="testpass123"
        )
        cls.user_with_mentor = User.objects.create_user(
            username="has_mentor",
            password="testpass123"
        )
        cls.user_with_both = User.objects.create_user(
            username="has_both",
            password="testpass123"
        )
        cls.mentee1 = User.objects.create_user(
            username="mentee1",
            password="testpass123"
        )
        cls.mentee2 = User.objects.create_user(
            username="mentee2",
            password="testpass123"
        )

        cls.user_with_mentees.mentees.add(cls.mentee1, cls.mentee2)
        cls.user_with_mentor.mentor = cls.user_with_mentees
        cls.user_with_mentor.save()
        cls.user_with_both.mentor = cls.user_with_mentees
        cls.user_with_both.save()
        cls.user_with_both.mentees.add(cls.mentee1)

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

    def test_registration_success(self):
        initial_count = User.objects.count()
        payload = {
            "username": "testuser2",
            "password": "testpassword2",
            "email": "testuser2@example.com",
            "phone_number": "+79991234567",
        }

        response = self.client.post(self.urls["registration"], payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), initial_count + 1)

    def test_registration_success_without_phone_number_and_email(self):
        initial_count = User.objects.count()
        payload = {
            "username": "testuser2",
            "password": "testpassword2",
        }

        response = self.client.post(self.urls["registration"], payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), initial_count + 1)
        self.assertEqual(User.objects.last().email, "")

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

    def test_user_list_success(self):
        response = self.client.get(self.urls["users"])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 7)
        self.assertIn("no_relations", [user["username"] for user in response.data])
        self.assertIn("has_mentees", [user["username"] for user in response.data])
        self.assertIn("has_mentor", [user["username"] for user in response.data])
        self.assertIn("has_both", [user["username"] for user in response.data])
        self.assertIn("mentee1", [user["username"] for user in response.data])
        self.assertIn("mentee2", [user["username"] for user in response.data])
        self.assertEqual(len([user for user in response.data if user["is_mentor"]]), 2)
        