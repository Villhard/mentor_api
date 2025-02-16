from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

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

        cls.test_user = User.objects.create_user(
            username="test_user",
            password="testpassword",
        )
        cls.user_with_mentees = User.objects.create_user(
            username="has_mentees", password="testpass123"
        )
        cls.user_with_mentor = User.objects.create_user(
            username="has_mentor", password="testpass123"
        )
        cls.user_with_both = User.objects.create_user(
            username="has_both", password="testpass123"
        )
        cls.mentee1 = User.objects.create_user(
            username="mentee1", password="testpass123"
        )
        cls.mentee2 = User.objects.create_user(
            username="mentee2", password="testpass123"
        )

        cls.test_user_client = APIClient()

        cls.user_with_mentees.mentees.add(cls.mentee1, cls.mentee2)
        cls.user_with_mentor.mentor = cls.user_with_mentees
        cls.user_with_mentor.save()
        cls.user_with_both.mentor = cls.user_with_mentees
        cls.user_with_both.save()
        cls.user_with_both.mentees.add(cls.mentee1)

    def setUp(self):
        super().setUp()
        response = self.client.post(
            self.urls["login"],
            {
                "username": self.test_user.username,
                "password": "testpassword",
            },
            format="json",
        )
        self.access_token = response.data["access"]
        self.refresh_token = response.data["refresh"]
        self.test_user_client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access_token}")

    def test_registration_success(self):
        initial_count = User.objects.count()
        payload = {
            "username": "newuser",
            "password": "testpass123",
            "email": "newuser@example.com",
            "phone_number": "+79991234567",
        }

        response = self.client.post(self.urls["registration"], payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), initial_count + 1)
        self.assertEqual(User.objects.last().email, "newuser@example.com")
        self.assertEqual(User.objects.last().phone_number, "+79991234567")

    def test_registration_success_without_phone_number_and_email(self):
        initial_count = User.objects.count()
        payload = {
            "username": "newuser2",
            "password": "testpass123",
        }

        response = self.client.post(self.urls["registration"], payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), initial_count + 1)
        self.assertEqual(User.objects.last().email, "")

    def test_login_success(self):
        payload = {
            "username": self.test_user.username,
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

        response = self.test_user_client.post(self.urls["refresh"], payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertNotEqual(response.data["access"], self.access_token)

    def test_logout_success(self):
        payload = {
            "refresh": self.refresh_token,
        }

        response = self.test_user_client.post(self.urls["logout"], payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_refresh_failure_after_logout(self):
        payload = {
            "refresh": self.refresh_token,
        }
        self.client.post(self.urls["logout"], payload, format="json")

        response = self.test_user_client.post(self.urls["refresh"], payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_user_list_success(self):
        initial_count = User.objects.count()
        mentor_count = User.objects.filter(mentees__isnull=False).distinct().count()

        response = self.test_user_client.get(self.urls["users"])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["count"], initial_count)
        self.assertIn("test_user", [user["username"] for user in response.data["results"]])
        self.assertIn("has_mentees", [user["username"] for user in response.data["results"]])
        self.assertIn("has_mentor", [user["username"] for user in response.data["results"]])
        self.assertIn("has_both", [user["username"] for user in response.data["results"]])
        self.assertIn("mentee1", [user["username"] for user in response.data["results"]])
        self.assertIn("mentee2", [user["username"] for user in response.data["results"]])
        self.assertEqual(
            len([user for user in response.data["results"] if user["is_mentor"]]), mentor_count
        )

    def test_user_detail_success(self):
        user_id = self.test_user.id

        response = self.test_user_client.get(self.urls["user_detail"](user_id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.test_user.username)
        self.assertNotIn("mentor", response.data)
        self.assertNotIn("mentees", response.data)

    def test_user_with_mentor_detail_success(self):
        user_id = self.user_with_mentor.id
        mentor_username = self.user_with_mentor.mentor.username

        response = self.test_user_client.get(self.urls["user_detail"](user_id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user_with_mentor.username)
        self.assertNotIn("mentees", response.data)
        self.assertIn("mentor", response.data)
        self.assertEqual(response.data["mentor"], mentor_username)

    def test_user_with_mentees_detail_success(self):
        user_id = self.user_with_mentees.id
        mentees_count = self.user_with_mentees.mentees.count()
        mentees_usernames = [mentee.username for mentee in self.user_with_mentees.mentees.all()]

        response = self.test_user_client.get(self.urls["user_detail"](user_id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user_with_mentees.username)
        self.assertIn("mentees", response.data)
        self.assertEqual(len(response.data["mentees"]), mentees_count)
        self.assertEqual(
            sorted(response.data["mentees"]),
            sorted(mentees_usernames),
        )
    
    def test_user_with_both_detail_success(self):
        user_id = self.user_with_both.id
        mentees_count = self.user_with_both.mentees.count()
        mentees_usernames = [mentee.username for mentee in self.user_with_both.mentees.all()]
        mentor_username = self.user_with_both.mentor.username
        
        response = self.test_user_client.get(self.urls["user_detail"](user_id))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], self.user_with_both.username)
        self.assertIn("mentees", response.data)
        self.assertIn("mentor", response.data)
        self.assertEqual(len(response.data["mentees"]), mentees_count)
        self.assertEqual(response.data["mentor"], mentor_username)
        self.assertEqual(
            sorted(response.data["mentees"]),
            sorted(mentees_usernames),
        )

    def test_user_update_success(self):
        user_id = self.test_user.id
        payload = {
            "username": "updated_user",
            "email": "updated@example.com",
            "phone_number": "+79992345678",
            "mentor": self.user_with_mentees.username,
            "mentees": [self.mentee1.username, self.mentee2.username],
        }

        response = self.test_user_client.put(self.urls["user_detail"](user_id), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], payload["username"])
        self.assertEqual(response.data["email"], payload["email"])
        self.assertEqual(response.data["phone_number"], payload["phone_number"])
        self.assertEqual(response.data["mentor"], payload["mentor"])
        self.assertEqual(
            sorted(response.data["mentees"]),
            sorted(payload["mentees"]),
        )
        
        mentees = User.objects.filter(mentor=self.test_user)
        self.assertEqual(mentees.count(), len(payload["mentees"]))
        self.assertEqual(
            sorted(mentees.values_list("username", flat=True)),
            sorted(payload["mentees"]),
        )

    def test_user_update_password_success(self):
        user_id = self.test_user.id
        payload = {
            "old_password": "testpassword",
            "new_password": "newpassword",
        }

        response = self.test_user_client.put(self.urls["user_detail"](user_id), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        updated_user = User.objects.get(id=user_id)
        self.assertTrue(updated_user.check_password("newpassword"))

    def test_user_update_password_failure(self):
        user_id = self.test_user.id
        payload = {
            "old_password": "wrongpassword",
            "new_password": "newpassword",
        }

        response = self.test_user_client.put(self.urls["user_detail"](user_id), payload, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        updated_user = User.objects.get(id=user_id)
        self.assertTrue(updated_user.check_password("testpassword"))

    def test_registration_with_invalid_data(self):
        payloads = [
            {
                "username": "",  # пустой username
                "password": "testpass123",
            },
            {
                "username": "user",
                "password": "testpass123",
                "email": "invalid-email",  # неверный формат email
            },
            {
                "username": "user",
                "password": "testpass123",
                "phone_number": "123",  # неверный формат телефона
            },
        ]

        for payload in payloads:
            response = self.client.post(self.urls["registration"], payload, format="json")
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_update_other_user_forbidden(self):
        other_user = User.objects.create_user(
            username="other_user",
            password="testpass123"
        )
        payload = {
            "username": "hacked_user",
        }

        response = self.test_user_client.put(
            self.urls["user_detail"](other_user.id),
            payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        other_user.refresh_from_db()
        self.assertEqual(other_user.username, "other_user")

    def test_set_nonexistent_mentor(self):
        payload = {
            "mentor": "nonexistent_user"
        }

        response = self.test_user_client.put(
            self.urls["user_detail"](self.test_user.id),
            payload,
            format="json"
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
