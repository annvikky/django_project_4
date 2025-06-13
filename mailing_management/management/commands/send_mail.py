import time

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from mailing_management.models import Mailing, MailingAttempt, Message, Recipient

User = get_user_model()


class Command(BaseCommand):
    help = "Отправить письмо (по ID Message) определённым получателям (по email)"

    def add_arguments(self, parser):
        parser.add_argument("message_id", type=int, help="ID письма из модели Message")
        parser.add_argument(
            "emails", type=str, help="Список email получателей через запятую"
        )
        parser.add_argument(
            "user_id", type=int, help="ID пользователя-владельца рассылки"
        )

    def handle(self, *args, **options):
        message_id = options["message_id"]
        emails = [
            email.strip() for email in options["emails"].split(",") if email.strip()
        ]
        user_id = options["user_id"]

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise CommandError(f"Пользователь с ID {user_id} не найден.")

        try:
            message = Message.objects.get(id=message_id, user=user)
        except Message.DoesNotExist:
            raise CommandError(
                f"Письмо с ID {message_id} не найдено или не принадлежит пользователю."
            )

        recipients = Recipient.objects.filter(email__in=emails, user=user)
        if not recipients.exists():
            self.stdout.write(
                self.style.WARNING("Не найдено получателей с указанными email.")
            )
            return

        mailing = Mailing.objects.filter(message=message, user=user).first()
        if mailing:
            mailing.status = "Running"
            mailing.date_first_sending = timezone.now()
            mailing.save()

        from_email = getattr(settings, "EMAIL_HOST_USER", "no-reply@example.com")
        self.stdout.write(f"Отправка письма '{message.subject}' получателям:")

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
                sent_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f"Отправлено на {recipient.email}")
                )

                if mailing:
                    MailingAttempt.objects.create(
                        attempt_date=timezone.now(),
                        status="Successful",
                        status_response="Успешно отправлено",
                        mailing=mailing,
                    )

                time.sleep(1)

            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"Ошибка при отправке на {recipient.email}: {e}")
                )

                if mailing:
                    MailingAttempt.objects.create(
                        attempt_date=timezone.now(),
                        status="Unsuccessful",
                        status_response=str(e),
                        mailing=mailing,
                    )

        if mailing:
            mailing.date_end_sending = timezone.now()
            mailing.status = "Completed"
            mailing.save()
