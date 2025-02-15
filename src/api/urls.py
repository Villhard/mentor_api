from django.urls import path, include
from rest_framework.routers import SimpleRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)
from .views import UserViewSet
from .views import RegistrationView

router = SimpleRouter()
router.register("users", UserViewSet, basename="users")


app_name = "api"

urlpatterns = [
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("", include(router.urls)),
]
