from django.contrib import admin
from el_tinto.ses_sns.models import SNSNotification


class SNSNotificationAdmin(admin.ModelAdmin):
    pass


admin.site.register(SNSNotification, SNSNotificationAdmin)
