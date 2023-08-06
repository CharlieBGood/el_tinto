from django.contrib.messages import get_messages
from django.shortcuts import reverse
from django.test import TestCase
from rest_framework.status import HTTP_200_OK

from el_tinto.tests.utils import test_scheduler
from el_tinto.tests.mails.factories import DailyMailFactory
from el_tinto.tests.users.factories import EditorFactory
from el_tinto.utils.send_mail import schedule_mail


class TestCancelSendDailyMailAction(TestCase):

    def setUp(self):
        self.daily_mail = DailyMailFactory()

        self.test_scheduler = test_scheduler

        # Make sure scheduler is only initialized once
        if not self.test_scheduler.running:
            self.test_scheduler.start()

        self.data = {'action': 'cancel_send_daily_mail', '_selected_action': [self.daily_mail.id]}
        self.url = reverse('admin:mails_mail_changelist')

        self.editor = EditorFactory()
        self.client.force_login(self.editor)

    def test_cancel_send_daily_mail(self):
        schedule_mail(self.daily_mail, self.test_scheduler)

        self.assertEqual(len(self.test_scheduler.get_jobs()), 1)

        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(self.test_scheduler.get_jobs()), 0)

        self.daily_mail.refresh_from_db()

        self.assertFalse(self.daily_mail.programmed)
