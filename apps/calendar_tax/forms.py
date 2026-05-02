from django import forms

from .models import OrganizationType, TaxSystem


class BootstrapFormMixin:
    def _apply_bootstrap(self) -> None:
        for field in self.fields.values():
            classes = field.widget.attrs.get("class", "")
            if isinstance(field.widget, forms.Select):
                field.widget.attrs["class"] = (classes + " form-select").strip()
            else:
                field.widget.attrs["class"] = (classes + " form-control").strip()


class CalendarFilterForm(BootstrapFormMixin, forms.Form):
    org_type = forms.ChoiceField(label="Тип организации", choices=OrganizationType.choices, required=False)
    tax_system = forms.ChoiceField(label="Система налогообложения", choices=TaxSystem.choices, required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["org_type"].choices = [(choice[0], choice[1]) for choice in OrganizationType.choices]
        self.fields["tax_system"].choices = [(choice[0], choice[1]) for choice in TaxSystem.choices]
        self._apply_bootstrap()