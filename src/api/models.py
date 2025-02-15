from django.contrib.auth.models import AbstractUser
from django.db import models


class ApiUser(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    mentor = models.ForeignKey(
        "self",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="mentees",
    )

    @property
    def is_mentor(self):
        return self.mentees.exists()
