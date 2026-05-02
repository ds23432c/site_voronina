from django.urls import path

from . import views

app_name = "forum"

urlpatterns = [
    path("", views.index, name="index"),
    path("new/", views.post_create, name="create"),
    path("<slug:slug>/", views.detail, name="detail"),
    path("<slug:slug>/edit/", views.post_edit, name="edit"),
    path("<slug:slug>/like/", views.like_post, name="like"),
    path("comments/<int:pk>/like/", views.comment_like, name="comment_like"),
]