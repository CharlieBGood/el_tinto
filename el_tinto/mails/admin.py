from django.contrib import admin
from el_tinto.mails.admin_actions.cancel_send_daily_mail import cancel_send_daily_email
from el_tinto.mails.admin_actions.send_daily_mail import send_daily_mail
from el_tinto.mails.admin_actions.send_mail_to_best_users import send_email_to_best_users
from el_tinto.mails.admin_actions.test_send_daily_mail import test_send_daily_email
from el_tinto.mails.models import Mail, SentEmailsInteractions


@admin.register(Mail)
class MailsAdmin(admin.ModelAdmin):
    """"Mail Admin."""

    list_display = ['type', 'subject', 'created_at', 'created_by', 'programmed', 'sent_datetime']
    readonly_fields = ('sent_datetime', )
    actions = [send_daily_mail, test_send_daily_email, cancel_send_daily_email]

    def get_queryset(self, request):
        qs = super(MailsAdmin, self).get_queryset(request)
        return qs.exclude(tye=Mail.WELCOME)

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super(MailsAdmin, self).save_model(request, obj, form, change)


admin.site.site_header = "El Tinto Administrador"
admin.site.site_title = "El Tinto"
admin.site.index_title = "El Tinto"

# @admin.register(SentEmailsInteractions)
# class SentEMailsInteractionAdmin(admin.ModelAdmin):
#     """"Mail Admin."""
