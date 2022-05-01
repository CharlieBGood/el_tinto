from datetime import datetime

from django.core.mail import EmailMessage
from django.template import loader
from django.utils.safestring import mark_safe


def send_several_emails(mail, users):
    for user in users:
        send_email(
            mail.subject, 
            'testing_email.html', 
            {'html': mark_safe(mail.html), 'date': datetime.today().strftime("%d/%m/%Y")}, 
            [user.email],
        )
        mail.recipients.add(user)
        mail.save()

def send_email(subject, html_file, mail_data, emails, reply_to=None):
    """Send email from template."""
    template = loader.get_template(
        f'../templates/mailings/{html_file}'
    )
    html = template.render(mail_data)
    if reply_to:
        message_user = EmailMessage(
            subject, html, 'El Tinto <info@eltinto.xyz>', emails, reply_to=[reply_to, ]
        )
    else:
        message_user = EmailMessage(
            subject, html, 'El Tinto <info@eltinto.xyz>', emails
        )
    message_user.content_subtype = 'html'
    message_user.send(fail_silently=True)
