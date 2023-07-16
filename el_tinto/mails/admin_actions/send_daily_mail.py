import datetime
import logging
import os

from django.contrib import admin, messages
from django.utils import timezone
from el_tinto.users.models import User
from el_tinto.utils.date_time import convert_utc_to_local_datetime
from el_tinto.utils.decorators import only_one_instance
from el_tinto.utils.scheduler import schedule_mail, schedule_mail_checking
from datetime import timedelta

logger = logging.getLogger("mails")


@admin.action(description='Enviar correo diario')
@only_one_instance
def send_daily_mail(_, request, queryset):
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
    users = User.objects.filter(is_active=True)

    if (
        mail.dispatch_date > timezone.now() + timedelta(minutes=5) or
        os.getenv('DJANGO_CONFIGURATION') != 'Production'
    ):
        # if not mail.programmed:
        schedule_mail(mail, users)
        # schedule_mail_checking(mail)

        now_datetime = convert_utc_to_local_datetime(datetime.datetime.now())
        string_now_datatime = now_datetime.strftime("%H:%M:%S of %m/%d/%Y")
        logger.info(f'Mail {mail.id} was programmed by {request.user.email} to be sent at {string_now_datatime}')

        # else:
        #     messages.error(request, "You can not send an already programmed mail unless you cancel it")

    else:
        messages.error(request, "Programmed time must be at least 5 minutes greater than current time")

