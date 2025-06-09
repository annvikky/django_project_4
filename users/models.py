from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):

    username = models.CharField(max_length=150, null=True, blank=True)
    email = models.EmailField(unique=True, verbose_name="Email")
    is_confirmed = models.BooleanField(default=False)
    confirmation_token = models.CharField(max_length=255, null=True, blank=True)
    password_reset_token = models.CharField(max_length=255, null=True, blank=True)
    phone_number = models.CharField(
        max_length=15,
        verbose_name="Телефон",
        blank=True,
        null=True,
        help_text="Введите номер телефона",
    )
    avatar = models.ImageField(
        upload_to="users/avatars/",
        verbose_name="Аватар",
        blank=True,
        null=True,
        help_text="Загрузите аватар",
    )
    country = models.CharField(
        max_length=50,
        verbose_name="Страна",
        blank=True,
        null=True,
        help_text="Укажите страну",
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"
        permissions = [
            ("blocking_user", "Может заблокировать пользователя"),
            ("list_user", "Может смотреть пользователей"),
        ]

    ROLE_CHOICES = [
        ("user", "Пользователь"),
        ("manager", "Менеджер"),
    ]
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default="user",
        verbose_name="Роль",
        help_text="Выберите роль пользователя",
    )

    is_blocked = models.BooleanField(
        default=False,
        verbose_name="Заблокирован",
        help_text="Если включено, пользователь не сможет входить в систему",
    )

    def __str__(self):
        return self.email
