from django.contrib import admin, messages
from el_tinto.utils.scheduler import get_scheduler
from el_tinto.utils.decorators import only_one_instance


@admin.action(description='Cancel send daily email')
@only_one_instance('cancel_send_daily_email')
def cancel_send_daily_email(_, request, queryset):
    """
    Cancel already programmed daily email.
    If the mail has been sent already return an error message.

    :params:
    request: Request object
    queryset: Mail queryset

    :return: None
    """
    mail = queryset.first()

    if not mail.sent_datetime:
        scheduler = get_scheduler()
        scheduler.remove_job(str(mail.id))
        mail.programmed = False
        mail.save()
    else:
        messages.error("Can not cancel mail sending after mail has been sent")
