from django.urls import path

from .views import HealthCheckView, UserDetailView, UserListView

urlpatterns = [
    path("healthz", HealthCheckView.as_view(), name="healthz"),
    path("users", UserListView.as_view(), name="user-list"),
    path("users/<int:pk>", UserDetailView.as_view(), name="user-detail"),
]
