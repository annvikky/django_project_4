from django.urls import path

from . import views
from .views import (MailingDeleteView, MailingDetailView, MailingListView, MailingUpdateView, MessageCreateView,
                    MessageDeleteView, MessageDetailView, MessageListView, MessageUpdateView, RecipientCreateView,
                    RecipientDeleteView, RecipientDetailView, RecipientListView, RecipientUpdateView, send_mail_view)

app_name = "mailing_management"

urlpatterns = [
    path("", views.show_main_page, name="home"),
    path("recipients/", RecipientListView.as_view(), name="recipients_list"),
    path("recipients/create/", RecipientCreateView.as_view(), name="recipient_create"),
    path(
        "recipients/<int:pk>/", RecipientDetailView.as_view(), name="recipient_detail"
    ),
    path(
        "recipients/<int:pk>/delete/",
        RecipientDeleteView.as_view(),
        name="recipient_delete",
    ),
    path(
        "recipients/<int:pk>/update/",
        RecipientUpdateView.as_view(),
        name="recipient_update",
    ),
    path("messages/", MessageListView.as_view(), name="messages_list"),
    path("messages/create/", MessageCreateView.as_view(), name="message_create"),
    path("messages/<int:pk>/", MessageDetailView.as_view(), name="message_detail"),
    path(
        "messages/<int:pk>/delete/", MessageDeleteView.as_view(), name="message_delete"
    ),
    path(
        "messages/<int:pk>/update/", MessageUpdateView.as_view(), name="message_update"
    ),
    path("mailings/", MailingListView.as_view(), name="mailings_list"),
    # path('mailings/create/', MailingCreateView.as_view(), name='mailing_create'),
    path("mailings/<int:pk>/", MailingDetailView.as_view(), name="mailing_detail"),
    path(
        "mailings/<int:pk>/delete/", MailingDeleteView.as_view(), name="mailing_delete"
    ),
    path(
        "mailings/<int:pk>/update/", MailingUpdateView.as_view(), name="mailing_update"
    ),
    path("send-mail/", send_mail_view, name="send_mail"),
]
