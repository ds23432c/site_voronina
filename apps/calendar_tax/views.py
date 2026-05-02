from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse

from .forms import CalendarFilterForm
from .models import TaxDeadline


def _filtered_deadlines(form):
    queryset = TaxDeadline.objects.all()
    if form.is_valid():
        org_type = form.cleaned_data.get("org_type")
        tax_system = form.cleaned_data.get("tax_system")
        if org_type and org_type != "all":
            queryset = queryset.filter(Q(org_type=org_type) | Q(org_type="all"))
        if tax_system and tax_system != "all":
            queryset = queryset.filter(Q(tax_system=tax_system) | Q(tax_system="all"))
    return queryset.order_by("deadline_date", "title")


def _export_text(deadlines):
    lines = [
        "Налоговый календарь БухПомощник",
        "",
    ]
    for item in deadlines:
        lines.append(
            f"{item.deadline_date:%d.%m.%Y} — {item.title} "
            f"({item.get_org_type_display()}, {item.get_tax_system_display()})"
        )
        if item.description:
            lines.append(f"  {item.description}")
    if len(lines) == 2:
        lines.append("Нет сроков по заданным фильтрам.")
    return "\n".join(lines)


def index(request):
    form = CalendarFilterForm(request.GET or None)
    deadlines = _filtered_deadlines(form)
    export_query = request.GET.urlencode()
    export_url = reverse("calendar_tax:export")
    if export_query:
        export_url = f"{export_url}?{export_query}"
    return render(
        request,
        "calendar_tax/index.html",
        {
            "title": "Налоговый календарь",
            "form": form,
            "deadlines": deadlines,
            "export_url": export_url,
        },
    )


def export(request):
    form = CalendarFilterForm(request.GET or None)
    deadlines = _filtered_deadlines(form)
    export_text = _export_text(deadlines)

    if request.GET.get("download") == "1":
        response = HttpResponse(export_text, content_type="text/plain; charset=utf-8")
        response["Content-Disposition"] = 'attachment; filename="tax-calendar.txt"'
        return response

    export_query = request.GET.urlencode()
    download_url = reverse("calendar_tax:export")
    if export_query:
        download_url = f"{download_url}?{export_query}&download=1"
    else:
        download_url = f"{download_url}?download=1"

    return render(
        request,
        "calendar_tax/export.html",
        {
            "title": "Экспорт налогового календаря",
            "form": form,
            "export_text": export_text,
            "download_url": download_url,
        },
    )