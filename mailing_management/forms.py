from django import forms

from .models import Mailing, Message, Recipient


class RecipientForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    class Meta:
        model = Recipient
        fields = ["email", "name", "comment"]


class MessageForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})

    class Meta:
        model = Message
        fields = ["subject", "body"]


# class MailingForm(forms.ModelForm):
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         for field in self.fields.values():
#             field.widget.attrs.update({'class': 'form-control'})
#
#     class Meta:
#         model = Mailing
#         fields = ['message',]
#
#     message = forms.ModelChoiceField(queryset=Message.objects.all(), label="Выберите письмо")
#     recipients = forms.ModelMultipleChoiceField(
#         queryset=Recipient.objects.all(),
#         widget=forms.CheckboxSelectMultiple,
#         label="Выберите получателей"
#     )


class MailingForm(forms.ModelForm):
    recipient = forms.ModelMultipleChoiceField(
        queryset=Recipient.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        label="Выберите получателей",
    )

    class Meta:
        model = Mailing
        fields = ["message", "recipient"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({"class": "form-control"})
        # Для поля recipients удобнее убрать класс, чтобы чекбоксы нормально выглядели
        self.fields["recipient"].widget.attrs.pop("class", None)
