from django.contrib import admin, messages

from el_tinto.users.models import User
from el_tinto.utils.decorators import only_one_instance


@admin.action(description='Enviar correo de prueba')
@only_one_instance
def send_daily_mail_try(_, request, queryset):
    """
    Send a mails mail to the user in the email field defined as 'test_email'
    If tested email is not in db, returns error message.

    :params:
    request: Request object
    queryset: Mails queryset

    :return: None
    """
    instance = queryset.first()

    try:
        user = User.objects.get(email=instance.test_email)
    except User.DoesNotExist:
        return messages.error(request, "Test email does not exist in the database")

    mail = instance.get_mail_class()

    mail.send_mail(user, test=True)
