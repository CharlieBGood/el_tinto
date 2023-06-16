from celery import shared_task
from el_tinto.mails.models import Mail
from el_tinto.users.models import User


@shared_task()
def send_mails_batch(users_emails_list, mail_id, week_day):
    """
    Send a batch of emails.

    :params:
    users_id_list: [dict]
    mail_id: int
    week_day: int
    """
    from el_tinto.utils.send_mail import send_todays_mail, send_mail

    users_list = User.objects.filter(email__in=users_emails_list)
    mail = Mail.objects.get(id=mail_id)

    for user in users_list:

        send_today = send_todays_mail(mail, user, week_day)

        if send_today:
            send_mail(mail, [user.email], user=user)
            mail.recipients.add(user)
            mail.save()

            if mail.dispatch_date.date().weekday() == 6 and user.missing_sunday_mails > 0:
                user.missing_sunday_mails -= 1
                user.save()
