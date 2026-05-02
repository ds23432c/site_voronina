from decimal import Decimal

from django import forms


class BootstrapFormMixin:
    def _apply_bootstrap(self) -> None:
        for field in self.fields.values():
            classes = field.widget.attrs.get("class", "")
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = (classes + " form-select").strip()
            else:
                field.widget.attrs["class"] = (classes + " form-control").strip()


class DocumentFillForm(BootstrapFormMixin, forms.Form):
    company_name = forms.CharField(label="Название организации", max_length=255)
    contractor_name = forms.CharField(label="Контрагент / исполнитель", max_length=255, required=False)
    employee_name = forms.CharField(label="ФИО сотрудника", max_length=255, required=False)
    recipient_name = forms.CharField(label="Кому адресован документ", max_length=255, required=False)
    director_name = forms.CharField(label="Подписант", max_length=255, required=False)
    position = forms.CharField(label="Должность", max_length=255, required=False)
    document_number = forms.CharField(label="Номер документа", max_length=64, required=False)
    document_date = forms.DateField(
        label="Дата документа",
        widget=forms.DateInput(attrs={"type": "date"}),
        required=False,
    )
    city = forms.CharField(label="Город", max_length=255, required=False)
    service_name = forms.CharField(label="Предмет / услуга", max_length=255, required=False)
    amount = forms.DecimalField(
        label="Сумма, ₽",
        min_value=Decimal("0"),
        decimal_places=2,
        max_digits=14,
        required=False,
    )
    basis = forms.CharField(label="Основание", max_length=255, required=False)
    comment = forms.CharField(
        label="Дополнительный текст",
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={"rows": 4}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()