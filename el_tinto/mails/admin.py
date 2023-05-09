from django.contrib import admin
from el_tinto.mails.admin_actions.cancel_send_daily_mail import cancel_send_daily_email
from el_tinto.mails.admin_actions.edit_tinto_in_cms import edit_tinto_in_cms
from el_tinto.mails.admin_actions.send_daily_mail import send_daily_mail
from el_tinto.mails.admin_actions.test_send_daily_mail import test_send_daily_email
from el_tinto.mails.admin_actions.send_mail_to_best_users import send_email_to_best_users
from el_tinto.mails.models import Mail, Templates


@admin.register(Mail)
class MailsAdmin(admin.ModelAdmin):
    """"Mail Admin."""

    list_display = ['type', 'subject', 'created_at', 'created_by', 'programmed', 'sent_datetime']
    readonly_fields = ('sent_datetime', 'tinto')
    actions = [send_daily_mail, test_send_daily_email, cancel_send_daily_email, edit_tinto_in_cms, send_email_to_best_users]

    def get_queryset(self, request):
        qs = super(MailsAdmin, self).get_queryset(request)
        # return qs.exclude(type=Mail.WELCOME)
        return qs

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super(MailsAdmin, self).save_model(request, obj, form, change)

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        if request.user.groups.filter(name__in=['Editor', 'Founder']):
            return super(MailsAdmin, self).get_model_perms(request)
        else:
            return {}


@admin.register(Templates)
class TemplatesAdmin(admin.ModelAdmin):
    """"Templates Admin."""

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        if request.user.groups.filter(name__in=['Founder']):
            return super(TemplatesAdmin, self).get_model_perms(request)
        else:
            return {}


admin.site.site_header = "La Cafetera"
admin.site.site_title = "La Cafetera"
admin.site.index_title = "El Tinto"

# @admin.register(SentEmailsInteractions)
# class SentEMailsInteractionAdmin(admin.ModelAdmin):
#     """"Mail Admin."""
