import logging
import os

from django.contrib import admin, messages
from django.utils import timezone
from el_tinto.users.models import User
from el_tinto.utils.decorators import only_one_instance
from datetime import timedelta

from el_tinto.utils.send_mail import send_several_mails_new

logger = logging.getLogger("mails")


@admin.action(description='Enviar correo diario NUEVO')
@only_one_instance
def send_daily_mail_new(_, request, queryset):
    """
    Send daily mail.
    Mails are allowed to be sent only 5 minutes after the current time (only in production).
    If more than 1 mail is selected, returns error message.
    If email is already programmed, returns error message.

    :params:
    request: Request object
    queryset: Mails queryset

    :return: None
    """
    mail = queryset.first()
    users = User.objects.filter(is_active=True).values_list('email', flat=True)

    if (
        mail.dispatch_date > timezone.now() + timedelta(minutes=5) or
        os.getenv('DJANGO_CONFIGURATION') != 'Production'
    ):
        if not mail.programmed:
            send_several_mails_new(mail, users)

        else:
            messages.error(request, "You can not send an already programmed mail unless you cancel it")

    else:
        messages.error(request, "Programmed time must be at least 5 minutes greater than current time")

