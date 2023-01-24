import datetime
import logging

from django.contrib import admin, messages

from el_tinto.utils.date_time import convert_utc_to_local_datetime
from el_tinto.utils.decorators import only_one_instance
from el_tinto.utils.scheduler import scheduler

logger = logging.getLogger("mails")


@admin.action(description='Cancelar envío de correo')
@only_one_instance
def cancel_send_daily_email(_, request, queryset):
    """
    Cancel already programmed daily email.
    If the mail has been sent already return an error message.

    :params:
    request: Request object
    queryset: Mail queryset

    :return: None
    """
    mail = queryset.first()

    if not mail.sent_datetime:
        scheduler.remove_job(str(mail.id))
        scheduler.remove_job(f'{str(mail.id)}_check')
        mail.programmed = False
        mail.save()

        now_datetime = convert_utc_to_local_datetime(datetime.datetime.now())
        string_now_datatime = now_datetime.strftime("%H:%M:%S of %m/%d/%Y")
        logger.info(f'Mail {mail.id} sending was canceled by {request.user.email} at {string_now_datatime}')

    else:
        messages.error(request, "Can not cancel mail sending after mail has been sent")
