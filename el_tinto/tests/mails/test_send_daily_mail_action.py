import datetime
from datetime import time

from django.contrib.messages import get_messages
from django.shortcuts import reverse
from django.test import TestCase
from django.utils import timezone
from rest_framework.status import HTTP_200_OK

from el_tinto.tests.utils import test_scheduler
from el_tinto.tests.mails.factories import DailyMailFactory
from el_tinto.tests.users.factories import EditorFactory, UserFactory


class TestSendDailyMailAction(TestCase):

    def setUp(self):
        self.daily_mail = DailyMailFactory()
        self.data = {'action': 'send_daily_mail', '_selected_action': [self.daily_mail.id]}
        self.url = reverse('admin:mails_mail_changelist')

        self.test_scheduler = test_scheduler

        # Make sure scheduler is only initialized once
        if self.test_scheduler.running == False:
            self.test_scheduler.start()

        # Clean old jobs
        for job in self.test_scheduler.get_jobs():
            job.remove()

        self.editor = EditorFactory()
        self.client.force_login(self.editor)

    def test_send_daily_mail(self):
        """
        Send daily mail
        """
        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(self.test_scheduler.get_jobs()), 1)

        job = self.test_scheduler.get_jobs()[0]
        self.daily_mail.refresh_from_db()

        self.assertEqual(job.id, f"{self.daily_mail.id}_{self.daily_mail.dispatch_date.strftime('%H:%M:%S')}")
        self.assertEqual(job.next_run_time, self.daily_mail.dispatch_date)
        self.assertTrue(self.daily_mail.programmed)
        self.assertEqual(self.daily_mail.created_by, self.editor)

    def test_send_daily_mail_several_user_dispatch_times(self):
        """
        Send daily mail when users have different dispatch times
        """
        dispatch_times = self._create_daily_mail_users()

        response = self.client.post(self.url, self.data, follow=True)
        self.assertEqual(response.status_code, HTTP_200_OK)
        self.assertEqual(len(self.test_scheduler.get_jobs()), 4)

        self.daily_mail.refresh_from_db()
        self.assertTrue(self.daily_mail.programmed)

        first_job = self.test_scheduler.get_jobs()[0]
        self.assertEqual(first_job.id, f"{self.daily_mail.id}_{self.daily_mail.dispatch_date.strftime('%H:%M:%S')}")
        self.assertEqual(first_job.next_run_time, self.daily_mail.dispatch_date)

        second_job = self.test_scheduler.get_jobs()[1]
        second_job_naive_dispatch_date = datetime.datetime.combine(
            self.daily_mail.dispatch_date.date(), dispatch_times[0]
        )
        second_job_dispatch_date = timezone.make_aware(second_job_naive_dispatch_date)
        self.assertEqual(second_job.id, f"{self.daily_mail.id}_{dispatch_times[0].strftime('%H:%M:%S')}")
        self.assertEqual(second_job.next_run_time, second_job_dispatch_date)

        third_job = self.test_scheduler.get_jobs()[2]
        third_job_naive_dispatch_date = datetime.datetime.combine(
            self.daily_mail.dispatch_date.date(), dispatch_times[1]
        )
        third_job_dispatch_date = timezone.make_aware(third_job_naive_dispatch_date)
        self.assertEqual(third_job.id, f"{self.daily_mail.id}_{dispatch_times[1].strftime('%H:%M:%S')}")
        self.assertEqual(third_job.next_run_time, third_job_dispatch_date)

        fourth_job = self.test_scheduler.get_jobs()[3]
        fourth_job_naive_dispatch_date = datetime.datetime.combine(
            self.daily_mail.dispatch_date.date(), dispatch_times[2]
        )
        fourth_dispatch_date = timezone.make_aware(fourth_job_naive_dispatch_date)
        self.assertEqual(fourth_job.id, f"{self.daily_mail.id}_{dispatch_times[2].strftime('%H:%M:%S')}")
        self.assertEqual(fourth_job.next_run_time, fourth_dispatch_date)

    def test_send_already_programmed_mail(self):
        """
        Send a mail that was already programmed
        """
        self.daily_mail.programmed = True
        self.daily_mail.save()

        response = self.client.post(self.url, self.data, follow=False)
        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'You can not send an already programmed mail unless you cancel it')

    def test_send_two_mails_at_the_time(self):
        """
        Select two mails to send at the same time
        """
        daily_mail_2 = DailyMailFactory()

        self.data['_selected_action'] = [self.daily_mail.id, daily_mail_2.id]

        response = self.client.post(self.url, self.data, follow=False)

        self.assertEqual(len(self.test_scheduler.get_jobs()), 0)

        messages = list(get_messages(response.wsgi_request))

        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Only one Mail at the time is allowed')

    def _create_daily_mail_users(self):
        # Users without dispatch time
        UserFactory.create_batch(size=5)

        # Users with dispatch time at 7 am
        first_dispatch_time = time(7, 0)
        UserFactory.create_batch(size=5, dispatch_time=first_dispatch_time)

        # Users with dispatch time at 8 am
        second_dispatch_time = time(8, 0)
        UserFactory.create_batch(size=5, dispatch_time=second_dispatch_time)

        # Users with dispatch time at 9 pm
        third_dispatch_time = time(21, 0)
        UserFactory.create_batch(size=5, dispatch_time=third_dispatch_time)

        return first_dispatch_time, second_dispatch_time, third_dispatch_time
