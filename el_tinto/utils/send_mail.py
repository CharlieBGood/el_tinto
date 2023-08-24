from datetime import datetime

from el_tinto.mails.models import Mail


def send_multiple_mails(mail_id, dispatch_time):

    instance = Mail.objects.get(id=mail_id)
    mail = instance.get_mail_class()
    mail.send_several_mails(dispatch_time)


def schedule_mail(mail, scheduler, dispatch_time=None):
    """
    schedule mail sending.

    :params:
    mail: Mail object

    :return: None
    """
    dispatch_time_str = dispatch_time.strftime('%H:%M:%S') if dispatch_time else mail.dispatch_date.strftime('%H:%M:%S')

    run_date = datetime.combine(mail.dispatch_date.date(), dispatch_time) if dispatch_time else mail.dispatch_date

    scheduler.add_job(
        send_multiple_mails,
        trigger='date',
        run_date=run_date,
        args=[mail.id, dispatch_time],
        id=f"{mail.id}_{dispatch_time_str}"
    )

    mail.programmed = True
    mail.save()
