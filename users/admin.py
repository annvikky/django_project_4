from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import CustomUser


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ("email", "username", "is_staff", "is_active", "country")
    list_filter = ("is_staff", "is_active", "country")
    search_fields = ("email", "username", "phone_number")
    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            "Личная информация",
            {"fields": ("username", "phone_number", "avatar", "country")},
        ),
        (
            "Права доступа",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Подтверждение", {"fields": ("is_confirmed", "confirmation_token")}),
        ("Сброс пароля", {"fields": ("password_reset_token",)}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "email",
                    "username",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
