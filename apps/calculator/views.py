from decimal import Decimal

from django.contrib import messages
from django.shortcuts import render
from django.urls import reverse

from .forms import (
    ContributionsForm,
    NDFLForm,
    PeniForm,
    SalaryForm,
    USNForm,
    VATForm,
)
from .models import Calculation
from .services import (
    calculate_contributions,
    calculate_ndfl,
    calculate_peni,
    calculate_salary,
    calculate_usn,
    calculate_vat,
    format_money,
    format_percent,
)


def _jsonify(value):
    if isinstance(value, dict):
        return {key: _jsonify(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_jsonify(item) for item in value]
    if isinstance(value, tuple):
        return [_jsonify(item) for item in value]
    if isinstance(value, Decimal):
        return str(value)
    if hasattr(value, "isoformat"):
        return value.isoformat()
    return value


def _save_calculation(request, calculation_type: str, form_data: dict, result_data: dict) -> None:
    if request.user.is_authenticated:
        Calculation.objects.create(
            user=request.user,
            calculation_type=calculation_type,
            input_data=_jsonify(form_data),
            result_data=_jsonify(result_data),
        )


def index(request):
    cards = [
        ("НДФЛ", "Расчет налога на доходы по прогрессивной шкале 2024 года", reverse("calculator:ndfl")),
        ("Страховые взносы", "Единый тариф, пенсионные и дополнительные взносы", reverse("calculator:contributions")),
        ("УСН", "Доходы или доходы минус расходы с учетом минимального налога", reverse("calculator:usn")),
        ("НДС", "Начисление и выделение НДС по ставкам 20% и 10%", reverse("calculator:vat")),
        ("Пени", "Расчет пени по налоговой задолженности", reverse("calculator:peni")),
        ("Зарплата", "Чистая зарплата и стоимость сотрудника для работодателя", reverse("calculator:salary")),
    ]
    return render(request, "calculator/index.html", {"title": "Калькуляторы", "cards": cards})


def ndfl(request):
    form = NDFLForm(request.POST or None)
    result = None
    if request.method == "POST" and form.is_valid():
        result = calculate_ndfl(form.cleaned_data["income"])
        _save_calculation(request, Calculation.CalculationType.NDFL, form.cleaned_data, result)
    elif request.method == "POST":
        messages.error(request, "Проверьте введенные данные.")

    return render(
        request,
        "calculator/ndfl.html",
        {
            "title": "Калькулятор НДФЛ",
            "form": form,
            "result": result,
            "result_rows": (
                [
                    ("Доход", format_money(result["income"])),
                    ("НДФЛ", format_money(result["tax"])),
                    ("Доход после налога", format_money(result["net_income"])),
                    ("Средняя ставка", format_percent(result["average_rate"])),
                ]
                if result
                else []
            ),
            "description": "Прогрессивный расчет по ставкам 13% и 15% для 2024 года.",
        },
    )


def contributions(request):
    form = ContributionsForm(request.POST or None)
    result = None
    if request.method == "POST" and form.is_valid():
        result = calculate_contributions(form.cleaned_data["payroll"], form.cleaned_data["injury_rate"])
        _save_calculation(request, Calculation.CalculationType.CONTRIBUTIONS, form.cleaned_data, result)
    elif request.method == "POST":
        messages.error(request, "Проверьте введенные данные.")

    return render(
        request,
        "calculator/contributions.html",
        {
            "title": "Страховые взносы",
            "form": form,
            "result": result,
            "result_rows": (
                [
                    ("Фонд оплаты труда", format_money(result["payroll"])),
                    ("База для единого тарифа", format_money(result["base_limit"])),
                    ("Взносы по единому тарифу", format_money(result["unified"])),
                    ("Взносы на травматизм", format_money(result["injury"])),
                    ("Итого взносов", format_money(result["total"])),
                    ("Эффективная ставка", format_percent(result["effective_rate"])),
                ]
                if result
                else []
            ),
            "description": "Расчет взносов по единому тарифу 2024 года с отдельным тарифом на травматизм.",
        },
    )


def usn(request):
    form = USNForm(request.POST or None)
    result = None
    if request.method == "POST" and form.is_valid():
        result = calculate_usn(
            form.cleaned_data["income"],
            form.cleaned_data.get("expenses") or Decimal("0"),
            form.cleaned_data["tax_object"],
        )
        _save_calculation(request, Calculation.CalculationType.USN, form.cleaned_data, result)
    elif request.method == "POST":
        messages.error(request, "Проверьте введенные данные.")

    return render(
        request,
        "calculator/usn.html",
        {
            "title": "Калькулятор УСН",
            "form": form,
            "result": result,
            "result_rows": (
                [
                    ("Доходы", format_money(result["income"])),
                    ("Расходы", format_money(result["expenses"])),
                    ("Налоговая база", format_money(result["tax_base"])),
                    ("Налог по ставке", format_money(result["calculated_tax"])),
                    ("Минимальный налог", format_money(result["min_tax"])),
                    ("К уплате", format_money(result["tax"])),
                ]
                if result
                else []
            ),
            "description": "Для объекта «Доходы» применяется ставка 6%, для объекта «Доходы минус расходы» — 15% и минимальный налог 1%.",
        },
    )


def vat(request):
    form = VATForm(request.POST or None)
    result = None
    if request.method == "POST" and form.is_valid():
        result = calculate_vat(form.cleaned_data["amount"], form.cleaned_data["rate"], form.cleaned_data["mode"])
        _save_calculation(request, Calculation.CalculationType.VAT, form.cleaned_data, result)
    elif request.method == "POST":
        messages.error(request, "Проверьте введенные данные.")

    return render(
        request,
        "calculator/vat.html",
        {
            "title": "Калькулятор НДС",
            "form": form,
            "result": result,
            "result_rows": (
                [
                    ("Сумма", format_money(result["amount"])),
                    ("Ставка НДС", format_percent(result["rate"])),
                    ("Без НДС", format_money(result["net"])),
                    ("НДС", format_money(result["vat"])),
                    ("Сумма с НДС", format_money(result["total"])),
                ]
                if result
                else []
            ),
            "description": "Начисление или выделение НДС по ставкам 20% и 10%.",
        },
    )


def peni(request):
    form = PeniForm(request.POST or None)
    result = None
    if request.method == "POST" and form.is_valid():
        result = calculate_peni(form.cleaned_data["debt"], form.cleaned_data["days_overdue"], form.cleaned_data["key_rate"])
        _save_calculation(request, Calculation.CalculationType.PENI, form.cleaned_data, result)
    elif request.method == "POST":
        messages.error(request, "Проверьте введенные данные.")

    return render(
        request,
        "calculator/peni.html",
        {
            "title": "Калькулятор пени",
            "form": form,
            "result": result,
            "result_rows": (
                [
                    ("Сумма долга", format_money(result["debt"])),
                    ("Дней просрочки", result["days_overdue"]),
                    ("Ключевая ставка", format_percent(result["key_rate"])),
                    ("Пени", format_money(result["penalty"])),
                ]
                if result
                else []
            ),
            "description": "Пени считаются по 1/300 ключевой ставки в первые 30 дней и по 1/150 далее.",
        },
    )


def salary(request):
    form = SalaryForm(request.POST or None)
    result = None
    if request.method == "POST" and form.is_valid():
        result = calculate_salary(form.cleaned_data["gross_salary"], form.cleaned_data.get("bonus") or Decimal("0"))
        _save_calculation(request, Calculation.CalculationType.SALARY, form.cleaned_data, result)
    elif request.method == "POST":
        messages.error(request, "Проверьте введенные данные.")

    return render(
        request,
        "calculator/salary.html",
        {
            "title": "Калькулятор зарплаты",
            "form": form,
            "result": result,
            "result_rows": (
                [
                    ("Начисление", format_money(result["gross_salary"])),
                    ("Премия", format_money(result["bonus"])),
                    ("Общая сумма начислений", format_money(result["total_accrual"])),
                    ("НДФЛ", format_money(result["ndfl"])),
                    ("На руки", format_money(result["net_salary"])),
                    ("Страховые взносы работодателя", format_money(result["contributions"])),
                    ("Стоимость сотрудника", format_money(result["employer_cost"])),
                ]
                if result
                else []
            ),
            "description": "Расчет чистой зарплаты и полной стоимости сотрудника по правилам 2024 года.",
        },
    )