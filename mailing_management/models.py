from django.conf import settings
from django.db import models


class Recipient(models.Model):
    email = models.EmailField(
        unique=True, verbose_name="Email", help_text="Введите вашу электронную почту"
    )
    name = models.CharField(
        max_length=150, verbose_name="ФИО", help_text="Введите ваши ФИО"
    )
    comment = models.TextField(
        max_length=500,
        verbose_name="Комментарий",
        help_text="Введите комментарий",
        blank=True,
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        related_name="recipients",
    )

    def __str__(self):
        return f"{self.email} {self.name} {self.comment}"

    class Meta:
        verbose_name = "Получатель рассылки"
        verbose_name_plural = "Получатели рассылки"
        ordering = ["email", "name"]


class Message(models.Model):
    subject = models.CharField(max_length=100, verbose_name="Тема сообщения")
    body = models.TextField(blank=True, null=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        related_name="messages",
    )

    def __str__(self):
        return f"{self.subject} {self.body}"

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"


class Mailing(models.Model):
    date_first_sending = models.DateTimeField(
        verbose_name="Дата первой отправки", blank=True, null=True
    )
    date_end_sending = models.DateTimeField(
        verbose_name="Дата окончание отправки", blank=True, null=True
    )
    status = models.CharField(
        max_length=15,
        choices=[
            ("Created", "Created"),
            ("Running", "Running"),
            ("Completed", "Completed"),
        ],
    )
    message = models.ForeignKey(
        Message, on_delete=models.CASCADE, verbose_name="Сообщение"
    )
    recipient = models.ManyToManyField(Recipient)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Владелец",
        related_name="mailings",
    )

    def __str__(self):
        return f"{self.date_first_sending} {self.date_end_sending} {self.status}"

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ["id"]

    def total_attempts(self):
        return self.mailingattempt_set.count()

    def successful_attempts(self):
        return self.mailingattempt_set.filter(status="Successful").count()

    def failed_attempts(self):
        return self.mailingattempt_set.filter(status="Unsuccessful").count()

    def success_rate(self):
        total = self.total_attempts()
        return round(self.successful_attempts() / total * 100, 2) if total > 0 else 0

    def last_attempt_date(self):
        return (
            self.mailingattempt_set.order_by("-attempt_date").first().attempt_date
            if self.mailingattempt_set.exists()
            else None
        )


class MailingAttempt(models.Model):
    attempt_date = models.DateTimeField(verbose_name="Дата и время попытки отправки")
    status = models.CharField(
        max_length=15,
        choices=[("Successful", "Successful"), ("Unsuccessful", "Unsuccessful")],
    )
    status_response = models.TextField(blank=True, null=True)
    mailing = models.ForeignKey(
        Mailing, on_delete=models.CASCADE, verbose_name="Рассылка"
    )

    def __str__(self):
        return f"{self.attempt_date} {self.status}"

    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылки"
