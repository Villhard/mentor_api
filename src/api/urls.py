from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from .views import (
    RegistrationView,
    TokenBlacklistView,
    TokenObtainPairView,
    TokenRefreshView,
    UserDetailView,
    UserListView,
)

app_name = "api"

urlpatterns = [
    # API docs
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/",
        SpectacularSwaggerView.as_view(url_name="api:schema"),
        name="swagger",
    ),
    # API auth
    path("registration/", RegistrationView.as_view(), name="registration"),
    path("login/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("logout/", TokenBlacklistView.as_view(), name="token_blacklist"),
    # API users
    path("users/", UserListView.as_view(), name="users-list"),
    path("users/<int:pk>/", UserDetailView.as_view(), name="users-detail"),
]
