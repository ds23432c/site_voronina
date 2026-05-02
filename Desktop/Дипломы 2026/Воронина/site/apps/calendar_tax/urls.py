from django.urls import path

from . import views

app_name = "calendar_tax"

urlpatterns = [
    path("", views.index, name="index"),
    path("export/", views.export, name="export"),
]