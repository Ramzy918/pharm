from django.urls import path

from . import views

urlpatterns = [
    path("register/", views.RegisterView.as_view(), name="register"),
    path("me/", views.MeView.as_view(), name="users-me"),
    path("", views.UserListCreateView.as_view(), name="users-list"),
    path("<int:pk>/", views.UserDetailView.as_view(), name="users-detail"),
]
