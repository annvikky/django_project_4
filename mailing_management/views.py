from functools import wraps

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from mailing_management.forms import MailingForm, MessageForm, RecipientForm
from mailing_management.models import Mailing, MailingAttempt, Message, Recipient


class ManagersReadOnlyMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.groups.filter(name="Managers").exists():
            return HttpResponseForbidden("У вас нет прав на изменение данных.")
        return super().dispatch(request, *args, **kwargs)


def managers_read_only(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.groups.filter(name="Managers").exists():
            return HttpResponseForbidden("У вас нет прав на изменение данных.")
        return view_func(request, *args, **kwargs)

    return _wrapped_view


@managers_read_only
def send_mail_view(request):
    if request.method == "POST":
        form = MailingForm(request.POST)
        if form.is_valid():
            # Сохраняем рассылку в базу данных
            mailing = form.save(commit=False)
            mailing.user = request.user
            mailing.status = "Running"
            mailing.date_first_sending = timezone.now()
            mailing.save()
            form.save_m2m()

            message = form.cleaned_data["message"]
            recipients = form.cleaned_data["recipient"]
            from_email = getattr(settings, "EMAIL_HOST_USER", "no-reply@example.com")

            sent_count = 0

            for recipient in recipients:
                try:
                    personalized_text = (
                        f"Здравствуйте, {recipient.name}!\n\n"
                        f"{message.body}\n\n"
                        f"Комментарий: {recipient.comment}"
                    )
                    send_mail(
                        subject=message.subject,
                        message=personalized_text,
                        from_email=from_email,
                        recipient_list=[recipient.email],
                        fail_silently=False,
                    )
                    MailingAttempt.objects.create(
                        attempt_date=timezone.now(),
                        status="Successful",
                        status_response="Отправлено успешно",
                        mailing=mailing,
                    )
                    sent_count += 1
                except Exception as e:
                    # Неудачная попытка
                    MailingAttempt.objects.create(
                        attempt_date=timezone.now(),
                        status="Unsuccessful",
                        status_response=str(e),
                        mailing=mailing,
                    )
                    messages.error(
                        request, f"Ошибка при отправке на {recipient.email}: {e}"
                    )

            mailing.status = "Completed"
            mailing.date_end_sending = timezone.now()
            mailing.refresh_from_db()
            print("Последняя попытка:", mailing.last_attempt_date())
            mailing.save()

            if sent_count:
                messages.success(request, f"Отправлено {sent_count} писем.")

            return redirect("mailing_management:home")

    else:
        form = MailingForm()

    return render(request, "mailing_management/send_mail.html", {"form": form})


def show_main_page(request):
    """ " Контроллер для отображения страницы home."""
    total_mailings = Mailing.objects.count()
    # completed_mailings = Mailing.objects.filter(status='Completed').count()
    active_mailings = Mailing.objects.filter(
        status__in=["Running", "Completed"]
    ).count()
    unique_recipients = Recipient.objects.values("email").distinct().count()

    context = {
        "total_mailings": total_mailings,
        "active_mailings": active_mailings,
        "unique_recipients": unique_recipients,
    }
    return render(request, "mailing_management/home.html", context)


@method_decorator(cache_page(60 * 15), name="dispatch")
class RecipientListView(LoginRequiredMixin, ListView):
    model = Recipient
    template_name = "mailing_management/recipients_list.html"
    context_object_name = "recipients"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Recipient.objects.all()
        return Recipient.objects.filter(user=user)


class RecipientDetailView(LoginRequiredMixin, DetailView):
    model = Recipient
    template_name = "mailing_management/recipient_detail.html"
    context_object_name = "recipient"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Recipient.objects.all()
        return Recipient.objects.filter(user=user)


class RecipientCreateView(LoginRequiredMixin, ManagersReadOnlyMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing_management/recipient_form.html"
    success_url = reverse_lazy("mailing_management:recipients_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.groups.filter(name='Users').exists():
    #         return Recipient.objects.all()
    #     return Recipient.objects.filter(user=user)


class RecipientDeleteView(LoginRequiredMixin, ManagersReadOnlyMixin, DeleteView):
    model = Recipient
    template_name = "mailing_management/recipient_delete.html"
    context_object_name = "recipient"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Recipient.objects.all()
        return Recipient.objects.filter(user=user)


class RecipientUpdateView(LoginRequiredMixin, ManagersReadOnlyMixin, UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = "mailing_management/recipient_form.html"
    success_url = reverse_lazy("mailing_management:recipients_list")

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Recipient.objects.all()
        return Recipient.objects.filter(user=user)


@method_decorator(cache_page(60 * 15), name="dispatch")
class MessageListView(LoginRequiredMixin, ListView):
    model = Message
    template_name = "mailing_management/messages_list.html"
    context_object_name = "messages"

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.groups.filter(name='Users').exists():
    #         return Recipient.objects.all()
    #     return Recipient.objects.filter(user=user)

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Message.objects.all()
        return Message.objects.filter(user=user)


class MessageDetailView(LoginRequiredMixin, DetailView):
    model = Message
    template_name = "mailing_management/message_detail.html"
    context_object_name = "message"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Message.objects.all()
        return Message.objects.filter(user=user)


class MessageCreateView(LoginRequiredMixin, ManagersReadOnlyMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing_management/message_form.html"
    success_url = reverse_lazy("mailing_management:messages_list")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    # def get_queryset(self):
    #     user = self.request.user
    #     if user.groups.filter(name='Managers').exists():
    #         return Message.objects.all()
    #     return Message.objects.filter(user=user)


class MessageDeleteView(LoginRequiredMixin, ManagersReadOnlyMixin, DeleteView):
    model = Message
    template_name = "mailing_management/message_delete.html"
    context_object_name = "message"
    success_url = reverse_lazy("mailing_management:messages_list")

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Message.objects.all()
        return Message.objects.filter(user=user)


class MessageUpdateView(LoginRequiredMixin, ManagersReadOnlyMixin, UpdateView):
    model = Message
    form_class = MessageForm
    template_name = "mailing_management/message_form.html"
    success_url = reverse_lazy("mailing_management:messages_list")

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Message.objects.all()
        return Message.objects.filter(user=user)


@method_decorator(cache_page(60 * 15), name="dispatch")
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = "mailing_management/mailings_list.html"
    context_object_name = "mailings"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(user=user)


class MailingDetailView(LoginRequiredMixin, DetailView):
    model = Mailing
    template_name = "mailing_management/mailing_detail.html"
    context_object_name = "mailing"

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(user=user)


# class MailingCreateView(LoginRequiredMixin, CreateView):
#     model = Mailing
#     form_class = MailingForm
#     template_name = 'mailing_management/mailing_form.html'
#     success_url = reverse_lazy('mailing_management:mailings_list')
#
#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         mailing = form.save(commit=False)
#         mailing.save()
#         mailing.status = 'Created'
#         mailing.date_first_sending = timezone.now()
#         form.save_m2m()
#         return super().form_valid(form)


class MailingDeleteView(LoginRequiredMixin, ManagersReadOnlyMixin, DeleteView):
    model = Mailing
    template_name = "mailing_management/mailing_delete.html"
    context_object_name = "mailing"
    success_url = reverse_lazy("mailing_management:mailings_list")

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(user=user)


class MailingUpdateView(LoginRequiredMixin, ManagersReadOnlyMixin, UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = "mailing_management/mailing_form.html"
    success_url = reverse_lazy("mailing_management:mailings_list")

    def get_queryset(self):
        user = self.request.user
        if user.groups.filter(name="Managers").exists():
            return Mailing.objects.all()
        return Mailing.objects.filter(user=user)
