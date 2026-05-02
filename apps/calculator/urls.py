from django.urls import path

from . import views

app_name = "calculator"

urlpatterns = [
    path("", views.index, name="index"),
    path("ndfl/", views.ndfl, name="ndfl"),
    path("contributions/", views.contributions, name="contributions"),
    path("usn/", views.usn, name="usn"),
    path("vat/", views.vat, name="vat"),
    path("peni/", views.peni, name="peni"),
    path("salary/", views.salary, name="salary"),
]