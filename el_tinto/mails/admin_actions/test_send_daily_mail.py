from django.contrib import admin, messages

from el_tinto.users.models import User
from el_tinto.utils.decorators import only_one_instance
from el_tinto.utils.send_mail import send_mail


@admin.action(description='Enviar correo de prueba')
@only_one_instance
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

    send_mail(mail, [mail.test_email], user=user)
