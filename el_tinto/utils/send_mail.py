import datetime
import logging
import os
import time

from django.core.mail import EmailMessage
from django.template import loader
from django.utils import timezone
from django.utils.safestring import mark_safe

from el_tinto.mails.models import Mail
from el_tinto.users.models import User
from el_tinto.utils.date_time import get_string_date, convert_utc_to_local_datetime
from el_tinto.utils.utils import replace_words_in_sentence

logger = logging.getLogger("mails")


def send_several_mails(mail, users):
    """
    Send mail to several users

    :params:
    mail: Mail object
    users: User queryset

    :return: None
    """
    # This number is based on AWS SES limitations.
    # Is calculated as the maximum number of mails/s - 1 to make sure never surpass AWS email sending capability
    n = 79

    # Split total users into chunks of length n to send at most those emails per second
    users_chunked_list = [users[i:i + n] for i in range(0, len(users), n)]

    for users_list in users_chunked_list:
        for user in users_list:

            html_version = get_mail_template(mail, user)

            week_day = timezone.now().date().weekday()

            send_today = True if user.preferred_email_days and week_day in user.preferred_email_days else False

            if not user.preferred_email_days or send_today:
                send_mail(
                    mail,
                    html_version,
                    get_mail_template_data(mail, user),
                    [user.email],
                    user=user
                )
                mail.recipients.add(user)
                mail.save()

        time.sleep(1)

    now_datetime = convert_utc_to_local_datetime(datetime.datetime.now())
    string_now_datatime = now_datetime.strftime("%H:%M:%S of %m/%d/%Y")
    logger.info(f'Mail {mail.id} was successfully sent at {string_now_datatime}')
    mail.sent_datetime = now_datetime
    mail.programmed = True
    mail.save()


def send_mail(mail, html_file, mail_data, mail_address, user=None, reply_to=None):
    """
    Send mail from template.

    :params:
    mail: Mail object
    html_file: str
    mail_data: dict
    mail_address: [str]
    user: User object
    reply_to: str
    """
    template = loader.get_template(f'../templates/mailings/{html_file}')

    send_email_address = (
        '☕ El Tinto <info@eltinto.xyz>'
        if os.getenv('DJANGO_CONFIGURATION') == 'Production'
        else '☕ El Tinto Pruebas <pruebas@dev.eltinto.xyz>'
    )

    mail_data['env'] = ('dev.' if os.getenv('DJANGO_CONFIGURATION') == 'Development' else '')

    html = template.render(mail_data)

    message_user = EmailMessage(
        replace_words_in_sentence(mail.subject, user=user),
        html,
        send_email_address,
        mail_address,
        reply_to=[reply_to] if reply_to else ['info@eltinto.xyz'],
        headers={
            'X-SES-CONFIGURATION-SET': (
                'Engagement'
                if os.getenv('DJANGO_CONFIGURATION') == 'Production'
                else 'Engagement_dev'
            ),
            'EMAIL-ID': str(mail.id),
            'EMAIL-TYPE': mail.type
        }
    )

    message_user.content_subtype = 'html'
    message_user.send(fail_silently=True)


def send_warning_mail(mail):
    """
    Send a warning mail to all admins if mail was not sent at the correct time.

    :params:
    mail: Mail object

    :return: None
    """
    if not mail.sent_datetime:
        error_mail = Mail(subject='🚩🚩🚩 El correo de hoy no ha sido enviado!!! 🚩🚩🚩')
        send_mail(
            error_mail,
            'mail_not_sent.html',
            {},
            [user.email for user in User.objects.filter(is_active=True, is_staff=True)]
        )

        now_datetime = convert_utc_to_local_datetime(datetime.datetime.now())
        string_now_datatime = now_datetime.strftime("%H:%M:%S of %m/%d/%Y")
        logger.error(f'Mail {mail.id} sending failed at {string_now_datatime}')


def get_mail_template(mail, user):
    """
    Defines the mail template to be used based on the type of mail and the user customization.

    :params:
    mail: Mail object
    user: User object

    :return: str
    """
    if mail.version == Mail.DEFAULT_TESTING:
        return 'default.html'

    else:
        return 'daily_mail_with_days.html' if 0 < len(user.preferred_email_days) < 7 else 'daily_mail.html'


def get_mail_template_data(mail, user):
    """
    Get the dictionary with all the mail data used to replace in template

    :params:
    mail: Mail object
    user: User object

    :return:
    email_data: dict
    """
    mail_data = {
        'html': mark_safe(replace_words_in_sentence(mail.html, user=user)),
        'date': get_string_date(mail.dispatch_date.date()),
        'name': user.first_name,
        'social_media_date': mail.dispatch_date.date().strftime("%d-%m-%Y"),
        'email': user.email,
        'tweet': mail.tweet.replace(' ', '%20').replace('"', "%22"),
        'email_type': 'Dominguero' if mail.dispatch_date.date().weekday() == 6 else 'Diario',
        'subject_message': mail.subject_message
    }

    return mail_data
