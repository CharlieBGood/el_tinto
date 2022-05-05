import json
import logging
from collections import namedtuple
from datetime import datetime

from django.db import models

from el_tinto.utils.datetime import convert_ut_to_local_datetime
from el_tinto.mails.models import Mail, SendedEmails
from el_tinto.users.models import User

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
        """Attempt to see if this notification is any of use (Open).
        If so - creates SendedEmails instance for open rate tracking."""
        try:
            if self.data.get('Type') == "Notification":
                message = json.loads(self.data['Message'])
                event_type = message.get('eventType')
                if event_type == 'Open':
                    mail_data = message.get('mail')
                    
                    timestamp = mail_data.get('timestamp')
                    utc_open_date = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S.%fZ')
                    loca_datetime = convert_ut_to_local_datetime(utc_open_date)
                    
                    for header in mail_data['headers']:
                        if header['name'] == 'EMAIL-ID':
                            email_id = header['value']
                        if header['name'] == 'EMAIL-TYPE':
                            email_type = header['value']
                        if header['name'] == 'To':
                            user_email = header['value']
                    
                    if email_type == Mail.DAILY:
                        user = User.objects.get(email=user_email)
                        mail = Mail.objects.get(id=int(email_id))
                        SendedEmails.objects.create(
                            user=user,
                            mail=mail,
                            opened_date=loca_datetime
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
