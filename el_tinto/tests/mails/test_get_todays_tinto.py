from datetime import datetime

from rest_framework.reverse import reverse
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.test import APITestCase

from el_tinto.tests.mails.factories import DailyMailFactory, SundayMailFactory


class TestGetTodaysTinto(APITestCase):

    def setUp(self):
        self.daily_mail = DailyMailFactory()
        self.daily_mail_class = self.daily_mail.get_mail_class()

        self.sunday_mail = SundayMailFactory()
        self.sunday_mail_class = self.sunday_mail.get_mail_class()

        self.url = reverse('mails-get-todays-tinto')

    def test_get_daily_tinto(self):
        """
        Get daily Tinto
        """
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTP_200_OK)

        daily_mail_data = self.daily_mail_class.get_mail_template_data()
        html = self.daily_mail_class.template.render(daily_mail_data)

        self.assertEqual(response.data['html'], html)

    def test_get_daily_tinto_with_date(self):
        """
        Get daily tinto with a specific date
        """
        tintos_date = datetime(2025, 2, 3, 6, 0)  # Make sure is not sunday
        new_daily_mail = DailyMailFactory(dispatch_date=tintos_date)
        new_daily_mail_class = new_daily_mail.get_mail_class()

        response = self.client.get(self.url, {'date': tintos_date.strftime('%d-%m-%Y')})

        self.assertEqual(response.status_code, HTTP_200_OK)

        daily_mail_data = new_daily_mail_class.get_mail_template_data()
        html = new_daily_mail_class.template.render(daily_mail_data)

        self.assertEqual(response.data['html'], html)

    def test_get_daily_tinto_for_non_existing_date(self):
        """
        Get a daily tinto for a date where no tinto exists
        """
        tintos_date = datetime(2025, 2, 3, 6, 0)  # Make sure is not sunday

        response = self.client.get(self.url, {'date': tintos_date.strftime('%d-%m-%Y')})

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)

    def test_get_daily_tinto_with_wrong_date_format(self):
        """
        Get daily tinto sending a date in wrong format
        """
        tintos_date = datetime(2025, 2, 3, 6, 0)  # Make sure is not sunday

        response = self.client.get(self.url, {'date': tintos_date.strftime('%Y-%m-%d')})

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['date'], 'Datetime format is not allowed, use DD-MM-YYYYY')

    def test_get_sundays_tinto(self):
        """
        Get sunday's tinto
        """
        response = self.client.get(self.url, {'date': self.sunday_mail.dispatch_date.strftime('%d-%m-%Y')})

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
