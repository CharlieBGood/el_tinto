import datetime
import logging
import os
import random
import time

from django.core.mail import EmailMessage
from django.template import loader
from django.utils import timezone
from django.utils.safestring import mark_safe

from el_tinto.mails.models import Mail
from el_tinto.users.models import User
from el_tinto.utils.date_time import get_string_date, convert_utc_to_local_datetime
from el_tinto.utils.utils import replace_words_in_sentence, replace_special_characters_for_url_use, get_env_value

logger = logging.getLogger("mails")


def send_several_mails(mail, users):
    """
    Send mail to several users

    :params:
    mail: Mail object
    users: User queryset

    :return: None
    """
    dispatch_beginning = datetime.datetime.now()
    string_dispatch_beginning = convert_utc_to_local_datetime(dispatch_beginning).strftime("%H:%M:%S of %m/%d/%Y")

    # This number is based on AWS SES limitations.
    # Is calculated as the maximum number of mails/s - 1 to make sure never surpass AWS email sending capability
    n = 79

    # Split total users into chunks of length n to send at most those emails per second
    users_chunked_list = [users[i:i + n] for i in range(0, len(users), n)]

    week_day = convert_utc_to_local_datetime(timezone.now()).date().weekday()

    logger.info(f"For today's Email {string_dispatch_beginning} the dispatch times for every 79 emails is:")

    for users_list in users_chunked_list:
        for user in users_list:

            send_today = send_todays_mail(mail, user, week_day)

            if send_today:
                send_mail(mail, [user.email], user=user)
                mail.recipients.add(user)
                mail.save()

                if mail.dispatch_date.date().weekday() == 6 and user.missing_sunday_mails > 0:
                    user.missing_sunday_mails -= 1
                    user.save()

        time.sleep(1)

        dispatched_time = datetime.datetime.now()
        delta_time = dispatched_time - dispatch_beginning

        dispatch_beginning = dispatched_time

        logger.info(f"{delta_time} seconds")

    now_datetime = convert_utc_to_local_datetime(datetime.datetime.now())
    string_now_datatime = now_datetime.strftime("%H:%M:%S of %m/%d/%Y")

    logger.info(f'Mail {mail.id} was successfully sent at {string_now_datatime}')
    mail.sent_datetime = now_datetime
    mail.programmed = True
    mail.save()


def send_mail(mail, mail_address, user=None, reply_to=None, extra_mail_data=None):
    """
    Send mail from template.

    :params:
    mail: Mail object
    mail_address: [str]
    user: User object
    reply_to: str
    """
    html_file = get_mail_template(mail, user)

    template = loader.get_template(f'../templates/mailings/{html_file}')

    send_email_address = get_sending_mail_address(mail)

    mail_data = get_mail_template_data(mail, user, extra_mail_data)

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


def send_warning_mail(mail_id):
    """
    Send a warning mail to all admins if mail was not sent at the correct time.

    :params:
    mail_id: int

    :return: None
    """
    mail = Mail.objects.get(pk=mail_id)
    if not mail.sent_datetime:
        error_mail = Mail(subject='🚩🚩🚩 El correo de hoy no ha sido enviado!!! 🚩🚩🚩', type=Mail.DAILY_MAIL_NOT_SENT)
        send_mail(error_mail, [user.email for user in User.objects.filter(is_active=True, is_staff=True)])

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

    elif mail.type == Mail.MILESTONE:
        return 'milestones.html'

    elif mail.type == Mail.WELCOME:
        return 'onboarding.html'

    elif mail.type == Mail.DAILY_MAIL_NOT_SENT:
        return 'mail_not_sent.html'

    elif mail.type == Mail.CHANGE_PREFERRED_DAYS:
        return 'change_preferred_days.html'

    elif not user:
        return 'daily_mail_base.html'

    elif mail.dispatch_date.date().weekday() == 6:
        return 'sunday_mail.html'

    else:
        return 'daily_mail_with_days.html' if 0 < len(user.preferred_email_days) < 7 else 'daily_mail.html'


def get_mail_template_data(mail, user, extra_mail_data):
    """
    Get the dictionary with all the mail data used to replace in template

    :params:
    mail: Mail object
    user: User object
    extra_mail_data: dict

    :return:
    mail_data: dict
    """
    mail_data = {
        'html': mark_safe(replace_words_in_sentence(mail.html, user=user)),
        'date': get_string_date(mail.dispatch_date.date()),
        'name': user.user_name if user else '',
        'social_media_date': mail.dispatch_date.date().strftime("%d-%m-%Y"),
        'email': user.email if user else '',
        'tweet': replace_special_characters_for_url_use(mail.tweet),
        'subject_message': mail.subject_message,
        'referred_users_count': user.referred_users_count if user else 0,
        'referral_code': user.referral_code if user else '',
        'mail_version': True,
        'env': get_env_value(),
        'uuid': user.uuid if user else '',
        'missing_sunday_mails': user.missing_sunday_mails if user else 0,
        'has_sunday_mails_prize': user.has_sunday_mails_prize if user else True
    }

    if extra_mail_data:
        mail_data.update(extra_mail_data)

    return mail_data


def get_sending_mail_address(mail):
    """
    Get sending mail address based on mail type

    :params:
    mail: Mail object

    :return:
    sending_mail_address: dict
    """
    if mail.type == Mail.MILESTONE:
        return (
            '☕ El Tinto - CEO <alejandro@eltinto.xyz>'
            if os.getenv('DJANGO_CONFIGURATION') == 'Production'
            else '☕ El Tinto Pruebas - CEO <alejandro@dev.eltinto.xyz>'
        )

    else:
        return(
            '☕ El Tinto <info@eltinto.xyz>'
            if os.getenv('DJANGO_CONFIGURATION') == 'Production'
            else '☕ El Tinto Pruebas <info@dev.eltinto.xyz>'
        )


def send_todays_mail(mail, user, week_day):
    """
    Define if the specific mail should be sent for the user.

    :params:
    mail: Mail object
    user: User object
    week_day: int

    :return:
    send_mail: dict
    """
    is_week_day_selected_by_user = week_day in user.preferred_email_days

    if mail.type == Mail.SUNDAY and mail.version == Mail.SUNDAY_NO_REFERRALS_PRIZE and user.missing_sunday_mails == 0:
        has_sunday_mails_prize = user.has_sunday_mails_prize
        probability_is_positive = random.random() < user.open_rate

        return is_week_day_selected_by_user and probability_is_positive and not has_sunday_mails_prize

    elif mail.type == Mail.SUNDAY:
        has_sunday_mails_prize = user.has_sunday_mails_prize

        return is_week_day_selected_by_user and has_sunday_mails_prize

    else:
        return is_week_day_selected_by_user
