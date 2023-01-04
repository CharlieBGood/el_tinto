import time

from django.contrib import admin
from el_tinto.users.models import User
from el_tinto.utils.decorators import only_one_instance
from el_tinto.utils.send_mail import send_mail
from el_tinto.utils.utils import replace_words_in_sentence
from django.utils.safestring import mark_safe


@admin.action(description='Send email to best users')
@only_one_instance
# TODO: review the function. Do not use in production, needs generalization.
def send_email_to_best_users(_, request, queryset):
    """
    Send email to best users

    :params:
    request: Request object
    queryset: Mail queryset

    :return: None
    """
    mail = queryset.first()
    users = User.objects.filter(best_user=True)

    n = 13
    users_chunked_list = [users[i:i + n] for i in range(0, len(users), n)]

    for users_list in users_chunked_list:
        for user in users_list:
            html_version = 'survey.html'

            name = user.first_name if user.first_name else user.email.split('@')[0]
            mail.subject = mail.subject if user.first_name else 'Queremos hablar contigo'
            html = mail.html.replace('{{ name }}', name)

            send_mail(
                mail,
                html_version,
                {
                    'html': mark_safe(replace_words_in_sentence(html, user=user)),
                },
                [user.email],
                user=user
            )
            mail.recipients.add(user)
            mail.save()

    time.sleep(1)
