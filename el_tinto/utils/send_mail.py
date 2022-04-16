from django.core.mail import EmailMessage
from django.template import loader


def send_email(subject, html_file, mail_data, email, reply_to=None):
    """Send email from template."""
    template = loader.get_template(
        f'../templates/mailings/{html_file}'
    )
    html = template.render(mail_data)
    if reply_to:
        message_user = EmailMessage(
            subject, html, 'El Tinto <info@eltinto.xyz>', [email, ], reply_to=[reply_to, ]
        )
    else:
        message_user = EmailMessage(
            subject, html, 'El Tinto <info@eltinto.xyz>', [email, ]
        )
    message_user.content_subtype = 'html'
    message_user.send(fail_silently=False)
