from django import forms
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError

from .models import Organization, User


class BootstrapFormMixin:
    def _bootstrapify(self) -> None:
        for field in self.fields.values():
            widget = field.widget
            classes = widget.attrs.get("class", "")
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = f"{classes} form-check-input".strip()
            elif isinstance(widget, (forms.Select, forms.SelectMultiple)):
                widget.attrs["class"] = f"{classes} form-select".strip()
            else:
                widget.attrs["class"] = f"{classes} form-control".strip()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._bootstrapify()


class SignUpForm(BootstrapFormMixin, forms.ModelForm):
    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )
    password2 = forms.CharField(
        label="Подтвердите пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password"}),
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "role",
            "organization_type",
            "tax_system",
            "phone",
            "avatar",
        )
        widgets = {
            "email": forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "name@example.com"}),
            "first_name": forms.TextInput(attrs={"autocomplete": "given-name"}),
            "last_name": forms.TextInput(attrs={"autocomplete": "family-name"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel", "placeholder": "+7 (___) ___-__-__"}),
            "avatar": forms.URLInput(attrs={"placeholder": "https://example.com/avatar.jpg"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"].strip().lower()
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class LoginForm(BootstrapFormMixin, forms.Form):
    email = forms.EmailField(
        label="Электронная почта",
        widget=forms.EmailInput(attrs={"autocomplete": "email", "placeholder": "name@example.com"}),
    )
    password = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={"autocomplete": "current-password"}),
    )

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get("email")
        password = cleaned_data.get("password")
        if email and password:
            self.user_cache = authenticate(
                self.request,
                username=email.strip().lower(),
                password=password,
            )
            if self.user_cache is None:
                raise ValidationError("Неверная почта или пароль.")
            if not self.user_cache.is_active:
                raise ValidationError("Учётная запись отключена.")
        return cleaned_data

    def get_user(self):
        return self.user_cache


class ProfileForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = User
        fields = (
            "first_name",
            "last_name",
            "email",
            "phone",
            "role",
            "organization_type",
            "tax_system",
            "avatar",
        )
        widgets = {
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel"}),
            "avatar": forms.URLInput(attrs={"placeholder": "https://example.com/avatar.jpg"}),
        }

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        qs = User.objects.filter(email__iexact=email)
        if self.instance.pk:
            qs = qs.exclude(pk=self.instance.pk)
        if qs.exists():
            raise ValidationError("Пользователь с таким email уже существует.")
        return email


class OrganizationForm(BootstrapFormMixin, forms.ModelForm):
    class Meta:
        model = Organization
        fields = (
            "name",
            "organization_type",
            "tax_system",
            "inn",
            "kpp",
            "phone",
            "email",
            "address",
            "website",
            "description",
        )
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Например, ООО «Альфа»"}),
            "inn": forms.TextInput(attrs={"placeholder": "1234567890"}),
            "kpp": forms.TextInput(attrs={"placeholder": "123456789"}),
            "phone": forms.TextInput(attrs={"autocomplete": "tel"}),
            "email": forms.EmailInput(attrs={"autocomplete": "email"}),
            "website": forms.URLInput(attrs={"placeholder": "https://..."}),
            "description": forms.Textarea(attrs={"rows": 4}),
        }
