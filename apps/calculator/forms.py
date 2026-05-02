from decimal import Decimal

from django import forms


class BootstrapFormMixin:
    def _apply_bootstrap(self) -> None:
        for field in self.fields.values():
            widget = field.widget
            classes = widget.attrs.get("class", "")
            if isinstance(widget, (forms.CheckboxInput, forms.RadioSelect)):
                widget.attrs["class"] = (classes + " form-check-input").strip()
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = (classes + " form-select").strip()
            else:
                widget.attrs["class"] = (classes + " form-control").strip()


class NDFLForm(BootstrapFormMixin, forms.Form):
    income = forms.DecimalField(
        label="Годовой доход, ₽",
        min_value=Decimal("0"),
        decimal_places=2,
        max_digits=14,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class ContributionsForm(BootstrapFormMixin, forms.Form):
    payroll = forms.DecimalField(
        label="Фонд оплаты труда, ₽",
        min_value=Decimal("0"),
        decimal_places=2,
        max_digits=14,
    )
    injury_rate = forms.DecimalField(
        label="Тариф взносов на травматизм, %",
        min_value=Decimal("0"),
        max_value=Decimal("20"),
        decimal_places=2,
        max_digits=5,
        initial=Decimal("0.2"),
        help_text="Укажите процент без знака %",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["injury_rate"].widget.attrs["step"] = "0.1"
        self._apply_bootstrap()


class USNForm(BootstrapFormMixin, forms.Form):
    TAX_CHOICES = (
        ("income", "Доходы — 6%"),
        ("income_expenses", "Доходы минус расходы — 15%"),
    )

    tax_object = forms.ChoiceField(label="Объект налогообложения", choices=TAX_CHOICES)
    income = forms.DecimalField(
        label="Доходы, ₽",
        min_value=Decimal("0"),
        decimal_places=2,
        max_digits=14,
    )
    expenses = forms.DecimalField(
        label="Расходы, ₽",
        min_value=Decimal("0"),
        decimal_places=2,
        max_digits=14,
        initial=Decimal("0"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class VATForm(BootstrapFormMixin, forms.Form):
    RATE_CHOICES = (
        ("20", "20%"),
        ("10", "10%"),
    )
    MODE_CHOICES = (
        ("added", "Начислить НДС сверху"),
        ("included", "НДС уже включен в сумму"),
    )

    amount = forms.DecimalField(
        label="Сумма, ₽",
        min_value=Decimal("0"),
        decimal_places=2,
        max_digits=14,
    )
    rate = forms.ChoiceField(label="Ставка НДС", choices=RATE_CHOICES, initial="20")
    mode = forms.ChoiceField(label="Режим расчета", choices=MODE_CHOICES, initial="added")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class PeniForm(BootstrapFormMixin, forms.Form):
    debt = forms.DecimalField(
        label="Сумма задолженности, ₽",
        min_value=Decimal("0"),
        decimal_places=2,
        max_digits=14,
    )
    days_overdue = forms.IntegerField(
        label="Количество дней просрочки",
        min_value=1,
        max_value=3650,
    )
    key_rate = forms.DecimalField(
        label="Ключевая ставка ЦБ, %",
        min_value=Decimal("0"),
        max_value=Decimal("100"),
        decimal_places=2,
        max_digits=5,
        initial=Decimal("16"),
        help_text="Если ставка менялась, можно взять среднюю за период",
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()


class SalaryForm(BootstrapFormMixin, forms.Form):
    gross_salary = forms.DecimalField(
        label="Оклад / начисление, ₽",
        min_value=Decimal("0"),
        decimal_places=2,
        max_digits=14,
    )
    bonus = forms.DecimalField(
        label="Премия, ₽",
        min_value=Decimal("0"),
        decimal_places=2,
        max_digits=14,
        initial=Decimal("0"),
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()