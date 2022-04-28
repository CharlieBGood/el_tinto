from sched import scheduler
from django.contrib import admin
from .models import Mail
from el_tinto.users.models import User
from el_tinto.utils.send_mail import send_email, send_several_emails
from el_tinto.utils.scheduler import get_scheduler
from django.utils.safestring import mark_safe
from datetime import datetime

@admin.action(description='Send daily email')
def send_daily_email(modeladmin, request, queryset):
    mail = queryset.first()
    users = User.objects.filter(is_active=True)
    scheduler = get_scheduler()
    
    scheduler.add_job(send_several_emails, trigger='date', run_date=mail.dispatch_date, args=[mail, users])
    scheduler.start()
    
@admin.action(description='Test send daily email')
def test_send_daily_email(modeladmin, request, queryset):
    mail = queryset.first()
    send_email(
        mail.subject, 
        'testing_email.html', 
        {'html': mark_safe(mail.html), 'date': datetime.today().strftime("%d/%m/%Y")}, 
        [mail.test_email],
    )
    
@admin.action(description='Send daily emails to founders')
def send_daily_email_to_founders(modeladmin, request, queryset):
    mail = queryset.first()
    send_email(
        mail.subject, 
        'testing_email.html', 
        {'html': mark_safe(mail.html), 'date': datetime.today().strftime("%d/%m/%Y")}, 
        ['carlosbueno1196@gmail.com', 'a.lozada.c10@gmail.com'],
    )

@admin.register(Mail)
class MailsAdmin(admin.ModelAdmin):
    """"Mail Admin."""
    
    list_display = ['type', 'created_at', 'created_by']
    actions = [send_daily_email, test_send_daily_email, send_daily_email_to_founders]
    
    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super(MailsAdmin, self).save_model(request, obj, form, change)


