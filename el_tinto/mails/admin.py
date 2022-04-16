from django.contrib import admin
from .models import Mail
from el_tinto.utils.send_mail import send_email
from django.utils.safestring import mark_safe


@admin.action(description='Send daily email')
def send_daily_email(modeladmin, request, queryset):
    mail = queryset.first()
    send_email(
        mail.subject, 
        'testing_email.html', 
        {'html': mark_safe(mail.html)}, 
        'carlosbueno1196@gmail.com',
    )

@admin.register(Mail)
class MailsAdmin(admin.ModelAdmin):
    """"Mail Admin."""
    
    list_display = ['type', 'created_at', 'created_by']
    actions = [send_daily_email]
