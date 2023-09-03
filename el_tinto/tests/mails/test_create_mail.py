from datetime import datetime

import pytz
from rest_framework.reverse import reverse
from rest_framework.status import HTTP_201_CREATED
from rest_framework.test import APITestCase

from el_tinto.mails.models import Mail
from el_tinto.tests.tintos.factories import TintoFactory


class TestCreateMail(APITestCase):
    def setUp(self):
        self.tinto = TintoFactory()

        self.url = reverse('mails:mails-list')

    def test_create_daily_mail(self):
        """
        Successfully create a daily mail.
        """
        payload = {
            'tinto': self.tinto.id,
            'subject': 'Correo de prueba',
            'dispatch_date': datetime(2025, 2, 5, 6, 0),
            'tweet': 'test tweet'
        }

        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        mail = Mail.objects.filter(type=Mail.DAILY).first()
        self.assertEqual(mail.tinto, self.tinto)
        self.assertEqual(mail.version, Mail.A_VERSION)
        self.assertEqual(mail.subject, payload['subject'])
        self.assertEqual(mail.dispatch_date, payload['dispatch_date'].astimezone(pytz.utc))

    def test_create_daily_mail_with_specific_version(self):
        """
        Successfully create a daily mail with a specific version.
        """
        payload = {
            'tinto': self.tinto.id,
            'subject': 'Correo de prueba',
            'version': Mail.DEFAULT_TESTING_VERSION,
            'dispatch_date': datetime(2025, 2, 5, 6, 0),
            'tweet': 'test tweet'
        }

        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        mail = Mail.objects.filter(type=Mail.DAILY).first()
        self.assertEqual(mail.tinto, self.tinto)
        self.assertEqual(mail.version, Mail.DEFAULT_TESTING_VERSION)
        self.assertEqual(mail.subject, payload['subject'])
        self.assertEqual(mail.dispatch_date, payload['dispatch_date'].astimezone(pytz.utc))

    def test_create_daily_mail_with_specific_type(self):
        """
        Successfully create a daily mail with a specific version.
        """
        payload = {
            'tinto': self.tinto.id,
            'subject': 'Correo de prueba',
            'type': Mail.WELCOME,
            'version': Mail.DEFAULT_TESTING_VERSION,
            'dispatch_date': datetime(2025, 2, 5, 6, 0),
            'tweet': 'test tweet'
        }

        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        mail = Mail.objects.filter(type=Mail.WELCOME).first()
        self.assertEqual(mail.tinto, self.tinto)
        self.assertEqual(mail.version, Mail.DEFAULT_TESTING_VERSION)
        self.assertEqual(mail.subject, payload['subject'])
        self.assertEqual(mail.dispatch_date, payload['dispatch_date'].astimezone(pytz.utc))

    def test_create_sunday_mail(self):
        """
        Successfully create a sunday mail.
        """
        payload = {
            'tinto': self.tinto.id,
            'subject': 'Correo de prueba',
            'dispatch_date': datetime(2025, 2, 9, 6, 0),
            'tweet': 'test tweet'
        }

        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        mail = Mail.objects.filter(type=Mail.SUNDAY).first()
        self.assertEqual(mail.version, Mail.A_VERSION)
        self.assertEqual(mail.tinto, self.tinto)
        self.assertEqual(mail.subject, payload['subject'])
        self.assertEqual(mail.dispatch_date, payload['dispatch_date'].astimezone(pytz.utc))

        mail_no_prize = Mail.objects.filter(version=Mail.SUNDAY_NO_REFERRALS_PRIZE_VERSION).first()
        self.assertIsNone(mail_no_prize.tinto)
        self.assertEqual(mail_no_prize.subject, payload['subject'])
        self.assertEqual(mail_no_prize.dispatch_date, payload['dispatch_date'].astimezone(pytz.utc))
