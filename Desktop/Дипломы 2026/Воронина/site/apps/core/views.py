from django.contrib.auth import get_user_model
from django.db.models import F, Q
from django.shortcuts import get_object_or_404, render

from apps.accounts.models import Organization

from .forms import KnowledgeSearchForm
from .models import Article, ArticleCategory, Calculation

User = get_user_model()


def home_view(request):
    latest_articles = Article.objects.filter(is_published=True).order_by("-created_at")[:3]
    stats = {
        "users": User.objects.count(),
        "organizations": Organization.objects.count(),
        "calculations": Calculation.objects.count(),
        "articles": Article.objects.filter(is_published=True).count(),
    }
    features = [
        {
            "icon": "bi-graph-up-arrow",
            "title": "Финансовая аналитика",
            "text": "Быстрые расчёты, контроль показателей и наглядные подсказки для ежедневной работы.",
        },
        {
            "icon": "bi-file-earmark-text",
            "title": "Документы без ошибок",
            "text": "Пошаговые подсказки по первичке, договорам, актам и закрывающим документам.",
        },
        {
            "icon": "bi-calendar2-check",
            "title": "Календарь отчётности",
            "text": "Сроки, напоминания и контроль обязательных действий по налогам и взносам.",
        },
        {
            "icon": "bi-chat-dots",
            "title": "Умный чат",
            "text": "Поддержка с ответами на бухгалтерские вопросы на понятном русском языке.",
        },
        {
            "icon": "bi-shield-check",
            "title": "Проверки и риски",
            "text": "Сценарии действий при запросах ФНС, камеральных проверках и спорных ситуациях.",
        },
        {
            "icon": "bi-book",
            "title": "База знаний",
            "text": "Свежие статьи, чек-листы и материалы, которые помогают работать спокойнее и быстрее.",
        },
    ]
    return render(
        request,
        "core/home.html",
        {
            "latest_articles": latest_articles,
            "stats": stats,
            "features": features,
            "search_form": KnowledgeSearchForm(),
        },
    )


def _filter_articles(request):
    form = KnowledgeSearchForm(request.GET or None)
    articles = Article.objects.filter(is_published=True)
    query = ""
    category = ""
    category_label = ""

    if form.is_valid():
        query = form.cleaned_data.get("q", "").strip()
        category = form.cleaned_data.get("category", "")
        category_label = dict(ArticleCategory.choices).get(category, "")

        conditions = Q()
        if query:
            conditions &= Q(title__icontains=query) | Q(content__icontains=query) | Q(category__icontains=query)
        if category:
            conditions &= Q(category=category)
        if conditions:
            articles = articles.filter(conditions)

    return form, articles.order_by("-created_at"), query, category, category_label


def knowledge_list_view(request):
    form, articles, query, category, category_label = _filter_articles(request)
    return render(
        request,
        "core/knowledge_list.html",
        {
            "form": form,
            "articles": articles,
            "query": query,
            "category": category,
            "category_label": category_label,
            "category_label": category_label,
        },
    )


def knowledge_search_view(request):
    form, articles, query, category, category_label = _filter_articles(request)
    return render(
        request,
        "core/knowledge_search.html",
        {
            "form": form,
            "articles": articles,
            "query": query,
            "category": category,
        },
    )


def article_detail_view(request, slug):
    article = get_object_or_404(Article, slug=slug, is_published=True)
    Article.objects.filter(pk=article.pk).update(views_count=F("views_count") + 1)
    article.refresh_from_db(fields=["views_count"])
    related_articles = (
        Article.objects.filter(is_published=True)
        .exclude(pk=article.pk)
        .order_by("-created_at")[:3]
    )
    return render(
        request,
        "core/article_detail.html",
        {
            "article": article,
            "related_articles": related_articles,
        },
    )