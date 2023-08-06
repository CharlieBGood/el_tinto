from el_tinto.mails.models import Mail


def send_multiple_mails(mail_id):

    instance = Mail.objects.get(id=mail_id)
    mail = instance.get_mail_class()
    mail.send_several_mails()


def schedule_mail(mail, scheduler):
    """
    schedule mail sending.

    :params:
    mail: Mail object

    :return: None
    """
    scheduler.add_job(
        send_multiple_mails,
        trigger='date',
        run_date=mail.dispatch_date,
        args=[mail.id],
        id=str(mail.id)
    )

    mail.programmed = True
    mail.save()
