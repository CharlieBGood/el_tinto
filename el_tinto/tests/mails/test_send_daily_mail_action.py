from django.contrib.messages import get_messages
from django.shortcuts import reverse
from django.test import TestCase
from rest_framework.status import HTTP_200_OK

from el_tinto.tests.utils import test_scheduler
from el_tinto.tests.mails.factories import DailyMailFactory
from el_tinto.tests.users.factories import EditorFactory


class TestSendDailyMailAction(TestCase):

    def setUp(self):
        self.daily_mail = DailyMailFactory()
        self.data = {'action': 'send_daily_mail', '_selected_action': [self.daily_mail.id]}
        self.url = reverse('admin:mails_mail_changelist')

        self.test_scheduler = test_scheduler

        # Make sure scheduler is only initialized once
        if self.test_scheduler.running == False:
            self.test_scheduler.start()

        self.editor = EditorFactory()
        self.client.force_login(self.editor)

    def test_send_daily_mail(self):
        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(self.test_scheduler.get_jobs()), 1)

        job = self.test_scheduler.get_jobs()[0]
        self.daily_mail.refresh_from_db()

        self.assertEqual(job.id, str(self.daily_mail.id))
        self.assertEqual(job.next_run_time, self.daily_mail.dispatch_date)
        self.assertTrue(self.daily_mail.programmed)

    def test_send_already_programmed_mail(self):
        self.daily_mail.programmed = True
        self.daily_mail.save()

        response = self.client.post(self.url, self.data, follow=False)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You can not send an already programmed mail unless you cancel it')

    def test_send_two_mails_at_the_time(self):
        daily_mail_2 = DailyMailFactory()

        self.data['_selected_action'] = [self.daily_mail.id, daily_mail_2.id]

        response = self.client.post(self.url, self.data, follow=False)

        self.assertEqual(len(self.test_scheduler.get_jobs()), 0)

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Only one Mail at the time is allowed')
