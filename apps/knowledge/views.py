from django.db.models import F
from django.shortcuts import get_object_or_404, render

from .models import KnowledgeArticle


def index(request):
    featured_articles = KnowledgeArticle.objects.filter(is_published=True, is_featured=True)[:3]
    articles = KnowledgeArticle.objects.filter(is_published=True).order_by("-published_at", "-created_at")
    return render(
        request,
        "knowledge/index.html",
        {
            "featured_articles": featured_articles,
            "articles": articles,
        },
    )


def detail(request, slug):
    article = get_object_or_404(KnowledgeArticle, slug=slug, is_published=True)
    KnowledgeArticle.objects.filter(pk=article.pk).update(views_count=F("views_count") + 1)
    article.refresh_from_db(fields=["views_count"])
    return render(request, "knowledge/detail.html", {"article": article})