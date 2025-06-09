from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    def handle(self, *args, **options):
        user = get_user_model()
        user = User.objects.create(email="admin@mail.ru", name="Admin")
        user.set_password("admin")
        user.is_staff = (True,)
        user.is_superuser = (True,)
        user.save()
        self.stdout.write(
            self.style.success(
                f"Успешно создан суперпользователь с email: {user.email}"
            )
        )
