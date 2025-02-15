from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated

from .permissions import IsSelf
from .serializers import (
    RegistrationSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]


class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    queryset = User.objects.prefetch_related(
        Prefetch('mentees', queryset=User.objects.only('username'))
    )
    permission_classes = [IsAuthenticated]

class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.select_related('mentor').prefetch_related(
        Prefetch('mentees', queryset=User.objects.only('username'))
    )
    permission_classes = [IsAuthenticated, IsSelf]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserDetailSerializer
        return UserUpdateSerializer
