from django.contrib import admin, messages
from el_tinto.users.models import User
from el_tinto.utils.decorators import only_one_instance
from el_tinto.utils.send_mail import send_mail, get_mail_template, get_mail_template_data


@admin.action(description='Test send daily email')
@only_one_instance('test_send_daily_email')
def test_send_daily_email(_, request, queryset):
    """
    Send a test email to the user in the email field defined as 'test_email'
    If tested email is not in db, returns error message.

    :params:
    request: Request object
    queryset: Mails queryset

    :return: None
    """
    mail = queryset.first()

    try:
        user = User.objects.get(email=mail.test_email)
    except User.DoesNotExist:
        return messages.error(request, "Test email does not exist in the database")

    html_version = get_mail_template(mail, user)

    send_mail(
        mail,
        html_version,
        get_mail_template_data(mail, user),
        [mail.test_email],
        user=user
    )
