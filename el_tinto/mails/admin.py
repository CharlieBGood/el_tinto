import time

from django.contrib import admin, messages
from django.utils import timezone
from .models import Mail, SentEmailsInteractions
from el_tinto.users.models import User
from el_tinto.utils.datetime import get_string_date
from el_tinto.utils.send_mail import send_email, send_several_emails
from el_tinto.utils.scheduler import get_scheduler
from el_tinto.utils.utils import replace_words_in_sentence
from django.utils.safestring import mark_safe
from datetime import timedelta


@admin.action(description='Send daily email')
def send_daily_email(modeladmin, request, queryset):
    mail = queryset.first()
    users = User.objects.filter(is_active=True)

    if mail.dispatch_date > timezone.now() + timedelta(minutes=5):
        scheduler = get_scheduler()
        scheduler.add_job(
            send_several_emails,
            trigger='date',
            run_date=mail.dispatch_date,
            args=[mail, users],
            id=str(mail.id)
        )
        scheduler.start()
        mail.programmed = True
        mail.save()
    else:
        messages.error(request, "Programmed time must be at least 5 minutes greater than current time")


@admin.action(description='Cancel send daily email')
def cancel_send_daily_email(modeladmin, request, queryset):
    mail = queryset.first()
    scheduler = get_scheduler()
    scheduler.remove_job(mail.id)
    mail.programmed = False
    mail.save()


@admin.action(description='Send email to best users')
def send_email_to_best_users(modeladmin, request, queryset):
    mail = queryset.first()
    users = User.objects.filter(best_user=True)

    n = 13
    users_chunked_list = [users[i:i + n] for i in range(0, len(users), n)]

    for user in users_chunked_list:
        html_version = 'survey.html'

        send_email(
            mail,
            html_version,
            {
                'html': mark_safe(replace_words_in_sentence(mail.html, user=user)),
                'name': user.first_name if user.first_name else user.email.split('@')[0],
            },
            [user.email],
            user=user
        )
        mail.recipients.add(user)
        mail.save()

    time.sleep(1)


@admin.action(description='Test send daily email')
def test_send_daily_email(modeladmin, request, queryset):
    mail = queryset.first()

    try:
        user = User.objects.get(email=mail.test_email)
    except User.DoesNotExist:
        user = None

    html_version = 'daily_email.html'

    if mail.version == Mail.DEFUALT_TESTING:
        html_version = 'default.html'

    elif 0 < len(user.preferred_email_days) < 7:
        html_version = 'daily_email_with_days.html'

    send_email(
        mail,
        html_version,
        {
            'html': mark_safe(replace_words_in_sentence(mail.html, user=user)),
            'date': get_string_date(mail.dispatch_date.date()),
            'name': user.first_name if user else '',
            'social_media_date': mail.dispatch_date.date().strftime("%d-%m-%Y"),
            'email': user.email,
            'tweet': mail.tweet.replace(' ', '%20').replace('"', "%22"),
            'email_type': 'Dominguero' if mail.dispatch_date.date().weekday() == 6 else 'Diario'
        },
        [mail.test_email],
        user=user
    )


@admin.register(Mail)
class MailsAdmin(admin.ModelAdmin):
    """"Mail Admin."""

    list_display = ['type', 'subject', 'created_at', 'created_by', 'programmed']
    actions = [send_daily_email, test_send_daily_email, cancel_send_daily_email]

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super(MailsAdmin, self).save_model(request, obj, form, change)


@admin.register(SentEmailsInteractions)
class SentEMailsInteractionAdmin(admin.ModelAdmin):
    """"Mail Admin."""
