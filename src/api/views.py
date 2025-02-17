from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt import views as jwt_views

from .docs import docs_schemes
from .permissions import IsSelf
from .serializers import (
    RegistrationSerializer,
    UserDetailSerializer,
    UserListSerializer,
    UserUpdateSerializer,
)

User = get_user_model()


@docs_schemes["registration"]
class RegistrationView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer
    permission_classes = [AllowAny]
    authentication_classes = []


@docs_schemes["user_list"]
class UserListView(generics.ListAPIView):
    serializer_class = UserListSerializer
    queryset = User.objects.prefetch_related(
        Prefetch("mentees", queryset=User.objects.only("username"))
    )
    permission_classes = [IsAuthenticated]


@docs_schemes["user_detail"]
class UserDetailView(generics.RetrieveUpdateAPIView):
    queryset = User.objects.select_related("mentor").prefetch_related(
        Prefetch("mentees", queryset=User.objects.only("username"))
    )
    permission_classes = [IsAuthenticated, IsSelf]

    def get_serializer_class(self):
        if self.request.method == "GET":
            return UserDetailSerializer
        return UserUpdateSerializer


@docs_schemes["logout"]
class TokenBlacklistView(jwt_views.TokenBlacklistView):
    pass


@docs_schemes["login"]
class TokenObtainPairView(jwt_views.TokenObtainPairView):
    pass


@docs_schemes["refresh"]
class TokenRefreshView(jwt_views.TokenRefreshView):
    pass
