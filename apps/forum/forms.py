from django import forms

from .models import ForumComment, ForumPost


class ForumPostForm(forms.ModelForm):
    class Meta:
        model = ForumPost
        fields = ["title", "content", "categories", "is_published"]
        widgets = {
            "title": forms.TextInput(
                attrs={"class": "form-control", "placeholder": "Заголовок темы"}
            ),
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 10,
                    "placeholder": "Опишите вопрос, кейс или новость",
                }
            ),
            "categories": forms.SelectMultiple(attrs={"class": "form-select"}),
            "is_published": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["categories"].queryset = self.fields["categories"].queryset.order_by("name")
        self.fields["is_published"].required = False


class ForumCommentForm(forms.ModelForm):
    class Meta:
        model = ForumComment
        fields = ["content"]
        widgets = {
            "content": forms.Textarea(
                attrs={"class": "form-control", "rows": 4, "placeholder": "Ваш комментарий"}
            ),
        }