import datetime
import logging
import sys

from django.contrib import admin, messages
from django.db.models import Count

from el_tinto.mails.models import Mail
from el_tinto.tests.utils import test_scheduler
from el_tinto.users.models import User
from el_tinto.utils.date_time import convert_utc_to_local_datetime
from el_tinto.utils.decorators import only_one_instance

from el_tinto.utils.scheduler import scheduler
from el_tinto.utils.send_mail import schedule_mail

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

    # Define scheduler for testing
    mail_scheduler = test_scheduler if 'test' in sys.argv else scheduler

    if not mail.programmed:

        dispatch_times = User.objects.values('dispatch_time').annotate(dcount=Count('dispatch_time'))

        for dispatch_time in dispatch_times:
            schedule_mail(mail, mail_scheduler, dispatch_time['dispatch_time'])

        # Send no prize sunday mail
        try:
            no_prize_mail = Mail.objects.get(dispatch_date=mail.dispatch_date, version=Mail.SUNDAY_NO_REFERRALS_PRIZE)

            schedule_mail(no_prize_mail, mail_scheduler)

        except Mail.DoesNotExist:
            pass

        now_datetime = convert_utc_to_local_datetime(datetime.datetime.now())
        string_now_datatime = now_datetime.strftime("%H:%M:%S of %m/%d/%Y")
        logger.info(f'Mail {mail.id} was programmed by {request.user.email} to be sent at {string_now_datatime}')

        mail.created_by = request.user
        mail.save()

        mail_class = mail.get_mail_class()
        dispatch_users_count = mail_class.get_dispatch_users().count()

        messages.success(request, f"Correo programado para enviarse a {dispatch_users_count} usuarios")

    else:
        messages.error(request, "You can not send an already programmed mail unless you cancel it")
