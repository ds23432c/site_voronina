from django.urls import path

from . import views

app_name = "admin_panel"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("users/", views.users, name="users"),
    path("users/<int:pk>/", views.user_form, name="user_form"),
    path("articles/", views.articles, name="articles"),
    path("articles/new/", views.article_form, name="article_new"),
    path("articles/<int:pk>/", views.article_form, name="article_edit"),
    path("calendar/", views.calendar, name="calendar"),
    path("chats/", views.chats, name="chats"),
]