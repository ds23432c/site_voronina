from django.urls import path

from . import views

app_name = "chat"

urlpatterns = [
    path("", views.index, name="index"),
    path("history/", views.history, name="history"),
    path("clear/", views.clear_history, name="clear_history"),
    path("api/send/", views.send_message_api, name="api_send"),
]
