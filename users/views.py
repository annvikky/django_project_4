from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LogoutView
from django.core.mail import send_mail
# from django.shortcuts import redirect
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import cache_page
from django.views.generic import CreateView, DetailView, ListView
from django.views.generic.edit import UpdateView

from mailing_management.models import Mailing, MailingAttempt

from .forms import CustomUserCreationForm, EmailAuthenticationForm, ProfileForm, UserBlockForm
from .models import CustomUser


class ManagersOnlyMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.groups.filter(name="Managers").exists()

    def handle_no_permission(self):
        return HttpResponseForbidden("Доступ только для менеджеров.")


@method_decorator(cache_page(60 * 15), name="dispatch")
class UserListView(LoginRequiredMixin, ManagersOnlyMixin, ListView):
    model = CustomUser
    template_name = "users/user_list.html"
    context_object_name = "users"


@method_decorator(
    permission_required("users.blocking_user", raise_exception=True), name="dispatch"
)
class BlockUserView(UpdateView):
    model = CustomUser
    form_class = UserBlockForm
    template_name = "users/block_user_form.html"
    success_url = reverse_lazy("users:user_list")


class CustomUserLoginView(LoginView):
    authentication_form = EmailAuthenticationForm
    # model = CustomUser
    template_name = "users/login.html"
    # success_url = reverse_lazy("users:login")


class CustomUserLogoutView(LogoutView):
    model = CustomUser
    template_name = "users/logged_out.html"
    success_url = reverse_lazy("mailing_management:mailings_list")


class CustomUserProfileView(DetailView):
    model = CustomUser
    template_name = "users/profile.html"

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        mailings = Mailing.objects.filter(user=user)
        attempts = MailingAttempt.objects.filter(mailing__user=user)

        last_attempt = attempts.order_by("-attempt_date").first()

        context["total_mailings"] = mailings.count()
        context["successful_attempts"] = attempts.filter(status="Successful").count()
        context["unsuccessful_attempts"] = attempts.filter(
            status="Unsuccessful"
        ).count()
        context["total_attempts"] = attempts.count()
        context["last_attempt_date"] = (
            last_attempt.attempt_date if last_attempt else None
        )
        context["mailings_list_url"] = reverse("mailing_management:mailings_list")

        return context


class CustomUserProfileEditView(UpdateView):
    form_class = ProfileForm
    template_name = "users/edit_profile.html"

    def get_success_url(self):
        return reverse_lazy("users:profile")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Профиль успешно обновлён!")
        return super().form_valid(form)

    def get_object(self):
        return self.request.user


@method_decorator(login_required, name="dispatch")
class CustomUserProfileDeleteView(View):
    def get(self, request):
        return render(request, "users/confirm_delete.html")

    def post(self, request):
        user = request.user
        user.delete()
        messages.success(request, "Ваш профиль был удалён.")
        return redirect("users:login")


class RegisterView(CreateView):
    model = CustomUser
    form_class = CustomUserCreationForm
    template_name = "users/register.html"
    # success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save(commit=False)
        if not user.username:
            user.username = "user"
        user.is_active = False
        user.confirmation_token = get_random_string(64)
        user.save()
        users_group, created = Group.objects.get_or_create(name="Users")
        user.groups.add(users_group)
        self.send_email(user.email, user.confirmation_token)
        return render(self.request, "users/email_confirmation_required.html")

    def send_email(self, user_email, token):
        confirm_url = self.request.build_absolute_uri(
            reverse("users:confirm_email", kwargs={"token": token})
        )
        subject = "Подтверждение регистрации"
        message = f"Здравствуйте, подтвердите вашу почту по ссылке: {confirm_url}"
        from_email = settings.EMAIL_HOST_USER
        recipient_list = [user_email]
        send_mail(subject, message, from_email, recipient_list)


def confirm_email(request, token):
    user = get_object_or_404(CustomUser, confirmation_token=token)
    user.is_confirmed = True
    user.is_active = True
    user.confirmation_token = ""
    user.save()
    messages.success(request, "Почта успешно подтверждена. Теперь вы можете войти.")
    return redirect("users:login")
