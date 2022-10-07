import json
import logging
from collections import namedtuple

from django.db import models
from django.utils import timezone

from el_tinto.mails.models import Mail, SentEmails, SentEmailsInteractions
from el_tinto.users.models import User
from el_tinto.utils.utils import get_email_headers, EVENT_TYPE_CLICK, EVENT_TYPE_OPEN, EVENT_TYPES

logger = logging.getLogger(__name__)

NOTIFICATION_STATUSES = namedtuple('NOTIFICATION_STATUSES', 'new processed failed')._make(range(3))

class SNSNotification(models.Model):
    """Stores incoming notifications from SNS for later processing of bounces and complaints"""
    STATE_CHOICES = (
        (NOTIFICATION_STATUSES.new, "New"),
        (NOTIFICATION_STATUSES.processed, "Processed"),
        (NOTIFICATION_STATUSES.failed, "Failed"),

    )
    headers = models.JSONField(default=dict, )
    data = models.JSONField(default=dict, )
    added_dt = models.DateTimeField(auto_now_add=True, db_index=True)
    state = models.SmallIntegerField(default=NOTIFICATION_STATUSES.new, choices=STATE_CHOICES, db_index=True)
    last_processed_dt = models.DateTimeField(null=True, blank=True, db_index=True)
    processing_error = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        """Settings"""
        verbose_name = "SNS Notification"
        verbose_name_plural = "SNS Notifications"

    def __str__(self):
        return str(self.pk)

    def process(self):
        """Attempt to see if this notification is any of use (Open, Click).
        If so - creates SentEmails instance for open rate tracking."""
        try:
            if self.data.get('Type') == "Notification":
                message = json.loads(self.data['Message'])
                event_type = message.get('eventType')
                if event_type in EVENT_TYPES:
                    mail_data = message.get('mail')

                    headers = get_email_headers(mail_data['headers'])
                    
                    if headers.get('email_type') in [Mail.DAILY, Mail.PROMOTION, Mail.WELCOME]:
                        user = User.objects.get(email=headers.get('user_email'))
                        mail = Mail.objects.get(id=headers.get('email_id'))

                        if event_type == EVENT_TYPE_OPEN:
                            try:
                                sent_email = SentEmails.objects.get(
                                    user=user,
                                    mail=mail,
                                )
                                sent_email.opened_date = timezone.now()
                                sent_email.save()

                            except SentEmails.DoesNotExist:
                                pass

                        elif event_type == EVENT_TYPE_CLICK:
                            click_data = message.get('click')
                            try:
                                SentEmailsInteractions.objects.get(
                                    user=user,
                                    mail=mail,
                                    type=click_data['linkTags']['type'][0],

                                )

                            except SentEmailsInteractions.DoesNotExist:
                                SentEmailsInteractions.objects.create(
                                    user=user,
                                    mail=mail,
                                    link=click_data.get('link'),
                                    type=click_data['linkTags']['type'][0]
                                )

                else:
                    raise ValueError("Wrong type of notification")
            else:
                raise ValueError("Not a Notification")
        except Exception as e:
            logger.debug(f"Processing SNS Notification failed with {e}")
            self.state = NOTIFICATION_STATUSES.failed
            self.processing_error = str(e)
        self.save(update_fields=['state'])
