from django import forms


class BootstrapFormMixin:
    def _apply_bootstrap(self) -> None:
        for field in self.fields.values():
            classes = field.widget.attrs.get("class", "")
            if isinstance(field.widget, forms.Textarea):
                field.widget.attrs["class"] = (classes + " form-control").strip()
            else:
                field.widget.attrs["class"] = (classes + " form-control").strip()


class ChatMessageForm(BootstrapFormMixin, forms.Form):
    message = forms.CharField(
        label="Сообщение",
        widget=forms.Textarea(attrs={"rows": 2, "placeholder": "Опишите вопрос по бухгалтерии или налогам"}),
        max_length=4000,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_bootstrap()