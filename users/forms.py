from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.forms import BooleanField

from .models import CustomUser


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email", widget=forms.EmailInput(attrs={"autofocus": True})
    )


class StyleFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field, BooleanField):
                field.widget.attrs["class"] = "form-check-input"
            else:
                field.widget.attrs["class"] = "form-control"


class CustomUserCreationForm(StyleFormMixin, UserCreationForm):
    phone_number = forms.CharField(
        max_length=15,
        required=False,
        help_text="Необязательное поле. Введите ваш номер телефона.",
    )
    # username = forms.CharField(max_length=50, required=True)
    usable_password = None

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ("email", "password1", "password2")

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get("phone_number")
        if phone_number and not phone_number.isdigit():
            raise forms.ValidationError("Номер телефона должен содержать только цифры.")
        return phone_number


class UserBlockForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["is_active"]
        labels = {"is_active": "Активен"}


class ProfileForm(StyleFormMixin, forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["username", "email", "avatar", "phone_number", "country"]
