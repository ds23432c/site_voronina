from django import forms

from .models import ArticleCategory


class BootstrapFormMixin:
    def _bootstrapify(self):
        for field in self.fields.values():
            widget = field.widget
            classes = widget.attrs.get("class", "")
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = f"{classes} form-check-input".strip()
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = f"{classes} form-select".strip()
            else:
                widget.attrs["class"] = f"{classes} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapify()


class KnowledgeSearchForm(BootstrapFormMixin, forms.Form):
    q = forms.CharField(
        label="Поиск",
        required=False,
        widget=forms.TextInput(attrs={"placeholder": "Тема, вопрос, термин"}),
    )
    category = forms.ChoiceField(
        label="Категория",
        required=False,
        choices=(("", "Все категории"),) + tuple(ArticleCategory.choices),
    )
