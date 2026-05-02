from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_http_methods

from .forms import LoginForm, OrganizationForm, ProfileForm, SignUpForm


def _safe_next(request, fallback="accounts:dashboard"):
    next_url = request.POST.get("next") or request.GET.get("next")
    if next_url and url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        return next_url
    return fallback


@require_http_methods(["GET", "POST"])
def signup_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    form = SignUpForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user, backend="django.contrib.auth.backends.ModelBackend")
        messages.success(request, "Добро пожаловать в БухПомощник! Профиль создан.")
        return redirect("accounts:dashboard")

    return render(request, "accounts/signup.html", {"form": form})


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect("accounts:dashboard")

    form = LoginForm(request.POST or None, request=request)
    if request.method == "POST" and form.is_valid():
        login(request, form.get_user())
        messages.success(request, "Вы успешно вошли в систему.")
        return redirect(_safe_next(request))

    return render(
        request,
        "accounts/login.html",
        {"form": form, "next": request.POST.get("next") or request.GET.get("next", "")},
    )


def logout_view(request):
    logout(request)
    messages.info(request, "Вы вышли из аккаунта.")
    return redirect("core:home")


@login_required
@require_http_methods(["GET", "POST"])
def profile_view(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Профиль обновлён.")
        return redirect("accounts:profile")

    organizations = request.user.organizations.order_by("-created_at")
    calculations = request.user.calculator_calculations.order_by("-created_at")[:5]
    return render(
        request,
        "accounts/profile.html",
        {
            "form": form,
            "organizations": organizations,
            "calculations": calculations,
        },
    )


@login_required
def dashboard_view(request):
    organizations = request.user.organizations.order_by("-created_at")
    calculations = request.user.calculator_calculations.order_by("-created_at")[:5]
    context = {
        "organizations": organizations,
        "calculations": calculations,
        "organization_count": organizations.count(),
        "calculation_count": request.user.calculator_calculations.count(),
    }
    return render(request, "accounts/dashboard.html", context)


@login_required
@require_http_methods(["GET", "POST"])
def organization_form_view(request):
    organization = request.user.organizations.order_by("created_at").first()
    form = OrganizationForm(request.POST or None, instance=organization)
    if request.method == "POST" and form.is_valid():
        organization = form.save(commit=False)
        organization.owner = request.user
        organization.save()
        messages.success(request, "Данные организации сохранены.")
        return redirect("accounts:dashboard")

    return render(
        request,
        "accounts/organization_form.html",
        {
            "form": form,
            "organization": organization,
        },
    )
