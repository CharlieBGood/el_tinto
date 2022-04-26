from django.contrib import admin
from .models import Mail
from el_tinto.users.models import User
from el_tinto.utils.send_mail import send_email
from django.utils.safestring import mark_safe
from datetime import datetime


@admin.action(description='Send daily email')
def send_daily_email(modeladmin, request, queryset):
    mail = queryset.first()
    #TODO send different emails per user and send to everybody
    # TODO send email only to active users
    for user in User.objects.filter(active=True):
        send_email(
            mail.subject, 
            'testing_email.html', 
            {'html': mark_safe(mail.html), 'date': datetime.today().strftime("%d/%M/%Y")}, 
            [user.email],
        )
    
@admin.action(description='Test send daily email')
def test_send_daily_email(modeladmin, request, queryset):
    mail = queryset.first()
    send_email(
        mail.subject, 
        'testing_email.html', 
        {'html': mark_safe(mail.html), 'date': datetime.today().strftime("%d/%M/%Y")}, 
        [mail.test_email],
    )

@admin.register(Mail)
class MailsAdmin(admin.ModelAdmin):
    """"Mail Admin."""
    
    list_display = ['type', 'created_at', 'created_by']
    actions = [send_daily_email, test_send_daily_email]
    
    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super(MailsAdmin, self).save_model(request, obj, form, change)
