from django.urls import path

from . import views

app_name = "core"

urlpatterns = [
    path("", views.home_view, name="home"),
    path("knowledge/", views.knowledge_list_view, name="knowledge_list"),
    path("knowledge/search/", views.knowledge_search_view, name="knowledge_search"),
    path("knowledge/<slug:slug>/", views.article_detail_view, name="article_detail"),
]