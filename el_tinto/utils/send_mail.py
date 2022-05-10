import time
from datetime import datetime

from django.core.mail import EmailMessage
from django.template import loader
from django.utils.safestring import mark_safe


def send_several_emails(mail, users):
    
    n = 13
    users_chunked_list = [users[i:i + n] for i in range(0, len(users), n)] 
    
    for users_list in users_chunked_list:
        for user in users_list:
            send_email(
                mail, 
                'testing_email.html', 
                {
                    'html': mark_safe(mail.html), 
                    'date': datetime.today().strftime("%d/%m/%Y"),
                    'name': user.first_name
                }, 
                [user.email],
            )
            mail.recipients.add(user)
            mail.save()
        
        time.sleep(1)

def send_email(mail, html_file, mail_data, emails, reply_to=None):
    """Send email from template."""
    template = loader.get_template(
        f'../templates/mailings/{html_file}'
    )
    html = template.render(mail_data)
    if reply_to:
        message_user = EmailMessage(
            mail.subject, html, 'El Tinto <info@eltinto.xyz>', emails, reply_to=[reply_to, ],
            headers={
                'X-SES-CONFIGURATION-SET': 'Engagement',
                'EMAIL-ID': str(mail.id),
                'EMAIL-TYPE': mail.type
            }
        )
    else:
        message_user = EmailMessage(
            mail.subject, html, 'El Tinto <info@eltinto.xyz>', emails,
            headers={
                'X-SES-CONFIGURATION-SET': 'Engagement',
                'EMAIL-ID': str(mail.id),
                'EMAIL-TYPE': mail.type
            }
        )
    message_user.content_subtype = 'html'
    message_user.send(fail_silently=False)
