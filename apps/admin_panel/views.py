from functools import wraps

from django import forms
from django.apps import apps as django_apps
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.db.models import Count, Q
from django.db.models.functions import TruncDate
from django.forms import modelform_factory
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.views import redirect_to_login

from apps.knowledge.models import KnowledgeArticle


def _is_admin(user):
    return bool(user.is_authenticated and getattr(user, "role", "") == "admin")


def _admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path())
        if not _is_admin(request.user):
            raise PermissionDenied
        return view_func(request, *args, **kwargs)

    return wrapper


def _bootstrap_form(form):
    for field in form.fields.values():
        widget = field.widget
        existing = widget.attrs.get("class", "")
        if isinstance(widget, (forms.CheckboxInput, forms.CheckboxSelectMultiple)):
            widget.attrs["class"] = f"{existing} form-check-input".strip()
        elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
            widget.attrs["class"] = f"{existing} form-select".strip()
        else:
            widget.attrs["class"] = f"{existing} form-control".strip()
    return form


def _get_role_choices():
    User = get_user_model()
    try:
        role_field = User._meta.get_field("role")
    except Exception:
        role_field = None

    if role_field is not None and getattr(role_field, "choices", None):
        return role_field.choices

    return [
        ("user", "Пользователь"),
        ("manager", "Менеджер"),
        ("admin", "Администратор"),
    ]


class UserAdminForm(forms.Form):
    role = forms.ChoiceField(label="Роль", choices=())
    is_blocked = forms.BooleanField(label="Заблокирован", required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user_instance", None)
        super().__init__(*args, **kwargs)
        self.fields["role"].choices = _get_role_choices()

        if user is not None:
            self.fields["role"].initial = getattr(user, "role", "user")
            self.fields["is_blocked"].initial = bool(getattr(user, "is_blocked", False))

        _bootstrap_form(self)


def _build_article_form(instance=None, data=None):
    ArticleForm = modelform_factory(
        KnowledgeArticle,
        fields=["title", "excerpt", "content", "cover_url", "is_featured", "is_published"],
        widgets={
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "excerpt": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "content": forms.Textarea(attrs={"class": "form-control", "rows": 12}),
            "cover_url": forms.URLInput(attrs={"class": "form-control"}),
            "is_featured": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        },
    )
    return _bootstrap_form(ArticleForm(data=data, instance=instance))


def _find_app_model(app_label, preferred_names=None, field_candidates=None):
    preferred_names = preferred_names or []
    field_candidates = field_candidates or []

    try:
        app_config = django_apps.get_app_config(app_label)
    except LookupError:
        return None

    models = list(app_config.get_models())
    if not models:
        return None

    for name in preferred_names:
        for model in models:
            if model.__name__ == name:
                return model

    if field_candidates:
        for model in models:
            field_names = {field.name for field in model._meta.get_fields()}
            if any(all(candidate in field_names for candidate in group) for group in field_candidates):
                return model

    if len(models) == 1:
        return models[0]

    return None


def _field_value(obj, names, default=""):
    for name in names:
        value = getattr(obj, name, None)
        if value not in (None, ""):
            return str(value)
    return default


def _top_items(model, field_names, limit=5):
    if model is None:
        return []

    field = None
    for name in field_names:
        try:
            model._meta.get_field(name)
            field = name
            break
        except Exception:
            continue

    if field is None:
        return []

    return list(
        model.objects.values(field)
        .annotate(total=Count("id"))
        .order_by("-total", field)[:limit]
    )


def _top_labels(items):
    labels = []
    for item in items:
        for key, value in item.items():
            if key != "total":
                labels.append(value)
                break
    return labels


@_admin_required
def dashboard(request):
    User = get_user_model()
    has_date_joined = any(field.name == "date_joined" for field in User._meta.get_fields())
    if has_date_joined:
        registrations = (
            User.objects.filter(date_joined__isnull=False)
            .annotate(day=TruncDate("date_joined"))
            .values("day")
            .annotate(total=Count("id"))
            .order_by("day")
        )
    else:
        registrations = []

    calculator_model = _find_app_model(
        "calculator",
        preferred_names=["Calculation", "CalculationHistory", "CalculatorRecord", "CalculatorLog"],
        field_candidates=[["calculator_name"], ["name"], ["title"], ["topic"], ["calculator"]],
    )
    chat_session_model = _find_app_model(
        "chat",
        preferred_names=["ChatSession", "Conversation", "ChatThread"],
        field_candidates=[["topic"], ["subject"], ["title"], ["question"]],
    )

    popular_calculators = _top_items(
        calculator_model,
        ["calculator_name", "name", "title", "topic", "calculator"],
    )
    popular_chat_topics = _top_items(chat_session_model, ["topic", "subject", "title", "question"])

    role_field_exists = any(field.name == "role" for field in User._meta.get_fields())
    blocked_field_exists = any(field.name == "is_blocked" for field in User._meta.get_fields())

    calculator_labels = _top_labels(popular_calculators)
    calculator_values = [item["total"] for item in popular_calculators]
    topic_labels = _top_labels(popular_chat_topics)
    topic_values = [item["total"] for item in popular_chat_topics]

    context = {
        "user_count": User.objects.count(),
        "admin_count": User.objects.filter(role="admin").count() if role_field_exists else 0,
        "blocked_count": User.objects.filter(is_blocked=True).count() if blocked_field_exists else 0,
        "article_count": KnowledgeArticle.objects.count(),
        "registrations_labels": [item["day"].strftime("%d.%m") if item["day"] else "" for item in registrations],
        "registrations_values": [item["total"] for item in registrations],
        "popular_calculators_labels": calculator_labels,
        "popular_calculators_values": calculator_values,
        "popular_calculators_pairs": list(zip(calculator_labels, calculator_values)),
        "popular_topics_labels": topic_labels,
        "popular_topics_values": topic_values,
        "popular_topics_pairs": list(zip(topic_labels, topic_values)),
    }
    return render(request, "admin_panel/dashboard.html", context)


@_admin_required
def users(request):
    User = get_user_model()
    query = request.GET.get("q", "").strip()
    order_field = "-date_joined" if any(field.name == "date_joined" for field in User._meta.get_fields()) else "-pk"
    users_qs = User.objects.all().order_by(order_field)

    if query:
        search_fields = []
        for field_name in ("username", "email", "first_name", "last_name"):
            if any(field.name == field_name for field in User._meta.get_fields()):
                search_fields.append(Q(**{f"{field_name}__icontains": query}))
        if search_fields:
            expr = search_fields[0]
            for item in search_fields[1:]:
                expr |= item
            users_qs = users_qs.filter(expr)

    return render(request, "admin_panel/users.html", {"users": users_qs, "query": query})


@_admin_required
def user_form(request, pk):
    User = get_user_model()
    target_user = get_object_or_404(User, pk=pk)

    if request.method == "POST":
        form = UserAdminForm(request.POST, user_instance=target_user)
        if form.is_valid():
            if hasattr(target_user, "role"):
                target_user.role = form.cleaned_data["role"]
            if hasattr(target_user, "is_blocked"):
                target_user.is_blocked = form.cleaned_data["is_blocked"]
            target_user.save()
            messages.success(request, "Профиль пользователя обновлён.")
            return redirect("admin_panel:users")
    else:
        form = UserAdminForm(user_instance=target_user)

    return render(request, "admin_panel/user_form.html", {"form": form, "target_user": target_user})


@_admin_required
def articles(request):
    query = request.GET.get("q", "").strip()
    articles_qs = KnowledgeArticle.objects.all()
    if query:
        articles_qs = articles_qs.filter(title__icontains=query)

    return render(
        request,
        "admin_panel/articles.html",
        {"articles": articles_qs.order_by("-published_at"), "query": query},
    )


@_admin_required
def article_form(request, pk=None):
    article = get_object_or_404(KnowledgeArticle, pk=pk) if pk else None

    if request.method == "POST":
        form = _build_article_form(instance=article, data=request.POST)
        if form.is_valid():
            saved = form.save(commit=False)
            saved.save()
            form.save_m2m()
            messages.success(request, "Статья сохранена.")
            return redirect("admin_panel:articles")
    else:
        form = _build_article_form(instance=article)

    return render(request, "admin_panel/article_form.html", {"form": form, "article": article})


def _get_calendar_model():
    return _find_app_model(
        "calendar_tax",
        preferred_names=["CalendarEvent", "Event", "TaxCalendarEvent", "Deadline", "CalendarItem"],
        field_candidates=[
            ["title", "date"],
            ["title", "event_date"],
            ["title", "start"],
            ["title", "deadline"],
            ["name", "date"],
            ["name", "event_date"],
            ["name", "start"],
        ],
    )


def _calendar_form(model, instance=None, data=None):
    editable_fields = []
    for field in model._meta.fields:
        if field.primary_key or not field.editable:
            continue
        if getattr(field, "auto_now", False) or getattr(field, "auto_now_add", False):
            continue
        editable_fields.append(field.name)

    if not editable_fields:
        editable_fields = [field.name for field in model._meta.fields if field.editable and not field.primary_key]

    CalendarForm = modelform_factory(model, fields=editable_fields)
    return _bootstrap_form(CalendarForm(data=data, instance=instance))


@_admin_required
def calendar(request):
    model = _get_calendar_model()
    if model is None:
        return render(request, "admin_panel/calendar.html", {"events": [], "form": None, "model_missing": True})

    event_id = request.GET.get("event_id")
    instance = get_object_or_404(model, pk=event_id) if event_id else None

    if request.method == "POST":
        form = _calendar_form(model, instance=instance, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Событие календаря сохранено.")
            return redirect("admin_panel:calendar")
    else:
        form = _calendar_form(model, instance=instance)

    events = []
    for event in model.objects.all().order_by("-id")[:50]:
        events.append(
            {
                "object": event,
                "title": _field_value(event, ["title", "name", "subject"], str(event)),
                "date": _field_value(event, ["date", "event_date", "start", "deadline", "scheduled_for"]),
                "description": _field_value(event, ["description", "notes", "comment", "details"], ""),
            }
        )

    return render(
        request,
        "admin_panel/calendar.html",
        {
            "events": events,
            "form": form,
            "model_missing": False,
            "edit_instance": instance,
        },
    )


def _get_chat_models():
    session_model = _find_app_model(
        "chat",
        preferred_names=["ChatSession", "Conversation", "ChatThread"],
        field_candidates=[["topic"], ["subject"], ["title"], ["question"]],
    )
    message_model = _find_app_model(
        "chat",
        preferred_names=["ChatMessage", "Message", "ChatEntry"],
        field_candidates=[["content"], ["text"], ["message"], ["created_at"]],
    )
    return session_model, message_model


@_admin_required
def chats(request):
    session_model, message_model = _get_chat_models()
    sessions = []

    if session_model is not None:
        for session in session_model.objects.all().order_by("-id")[:50]:
            sessions.append(
                {
                    "object": session,
                    "topic": _field_value(session, ["topic", "subject", "title", "question"], str(session)),
                    "user": _field_value(session, ["user", "author", "created_by"], ""),
                    "created_at": getattr(session, "created_at", None),
                    "updated_at": getattr(session, "updated_at", None),
                    "summary": _field_value(session, ["summary", "last_message", "preview"], ""),
                }
            )

    return render(
        request,
        "admin_panel/chats.html",
        {
            "sessions": sessions,
            "session_model": session_model,
            "message_model": message_model,
        },
    )