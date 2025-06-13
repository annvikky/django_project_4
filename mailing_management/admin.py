from django.contrib import admin

from .models import Mailing, Message, Recipient


class ReadOnlyForManagersMixin:
    def has_add_permission(self, request):
        # Запретить добавление для менеджеров
        if request.user.groups.filter(name="Managers").exists():
            return False
        return super().has_add_permission(request)

    def has_change_permission(self, request, obj=None):
        # Запретить изменение для менеджеров
        if request.user.groups.filter(name="Managers").exists():
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        # Запретить удаление для менеджеров
        if request.user.groups.filter(name="Managers").exists():
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Recipient)
class RecipientAdmin(ReadOnlyForManagersMixin, admin.ModelAdmin):
    list_display = (
        "email",
        "name",
        "comment",
    )
    list_filter = (
        "email",
        "name",
    )
    search_fields = (
        "email",
        "name",
    )


@admin.register(Message)
class MessageAdmin(ReadOnlyForManagersMixin, admin.ModelAdmin):
    list_display = (
        "subject",
        "body",
    )
    list_filter = ("subject",)
    search_fields = ("subject",)


@admin.register(Mailing)
class MailingAdmin(ReadOnlyForManagersMixin, admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "total_attempts",
        "successful_attempts",
        "failed_attempts",
        "success_rate",
    )

    def total_attempts(self, obj):
        return obj.total_attempts()

    def successful_attempts(self, obj):
        return obj.successful_attempts()

    def failed_attempts(self, obj):
        return obj.failed_attempts()

    def success_rate(self, obj):
        return f"{obj.success_rate()}%"
