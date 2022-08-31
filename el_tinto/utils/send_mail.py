import os
import time

from django.core.mail import EmailMessage
from django.template import loader
from django.utils import timezone
from django.utils.safestring import mark_safe

from el_tinto.mails.models import Mail
from el_tinto.utils.utils import replace_words_in_sentence, get_string_days, DAY_OF_THE_WEEK_MAP


def send_several_emails(mail, users):
    
    n = 13
    users_chunked_list = [users[i:i + n] for i in range(0, len(users), n)]

    html_version = 'default.html' if mail.version == Mail.DEFUALT_TESTING else 'daily_email.html'

    for users_list in users_chunked_list:
        for user in users_list:

            if 0 < len(user.preferred_email_days) < 7:
                html_version = 'daily_email_with_days.html'

            week_day = timezone.now().date().weekday()

            send_today = True if user.preferred_email_days and week_day in user.preferred_email_days else False

            if not user.preferred_email_days or send_today:
                send_email(
                    mail,
                    html_version,
                    {
                        'html': mark_safe(replace_words_in_sentence(mail.html, user=user)),
                        'date': timezone.now().date().strftime("%d/%m/%Y"),
                        'name': user.first_name,
                        'social_media_date': mail.dispatch_date.date().strftime("%d-%m-%Y"),
                        'email': user.email,
                        'tweet': mail.tweet.replace(' ', '%20').replace('"', "%22")
                    },
                    [user.email],
                    user=user
                )
                mail.recipients.add(user)
                mail.save()
        
        time.sleep(1)

def send_email(mail, html_file, mail_data, emails, user=None, reply_to=None):
    """Send email from template."""
    template = loader.get_template(
        f'../templates/mailings/{html_file}'
    )
    sending_email_address = (
        '☕ El Tinto <info@eltinto.xyz>'
        if os.environ.setdefault("DJANGO_CONFIGURATION", "Production")
        else 'carlos@eltinto.xyz'
    )
    html = template.render(mail_data)
    if reply_to:
        message_user = EmailMessage(
            replace_words_in_sentence(mail.subject, user=user), html, sending_email_address, emails, reply_to=[reply_to, ],
            headers={
                'X-SES-CONFIGURATION-SET': 'Engagement',
                'EMAIL-ID': str(mail.id),
                'EMAIL-TYPE': mail.type
            }
        )
    else:
        message_user = EmailMessage(
            replace_words_in_sentence(mail.subject, user=user), html, sending_email_address, emails,
            headers={
                'X-SES-CONFIGURATION-SET': 'Engagement',
                'EMAIL-ID': str(mail.id),
                'EMAIL-TYPE': mail.type
            }
        )
    message_user.content_subtype = 'html'
    message_user.send(fail_silently=False)
