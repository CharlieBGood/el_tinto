import os
import urllib.parse
from datetime import timedelta, time

from django.core import mail
from django.template import loader
from django.test import TestCase

from el_tinto.mails.models import Mail
from el_tinto.tests.mails.factories import DailyMailFactory, SundayMailFactory, SentEmailsFactory
from el_tinto.tests.users.factories import UserFactory
from el_tinto.utils.date_time import get_string_date
from el_tinto.utils.utils import get_env_value, MILESTONES, replace_words_in_sentence, UTILITY_MAILS, \
    ONBOARDING_EMAIL_NAME, CHANGE_PREFERRED_DAYS


def get_mail_headers(headers_mail):
    return {
        'X-SES-CONFIGURATION-SET': (
            'Engagement'
            if os.getenv('DJANGO_CONFIGURATION') == 'Production'
            else 'Engagement_dev'
        ),
        'EMAIL-ID': str(headers_mail.id),
        'EMAIL-TYPE': headers_mail.type
    }


def get_template(template_name):
    template_path = f'../../mails/templates/mailings/{template_name}.html'

    return loader.get_template(template_path)


class TestMailClass(TestCase):
    fixtures = ['mails']

    def setUp(self):
        self.daily_mail = DailyMailFactory()
        self.daily_mail_class = self.daily_mail.get_mail_class()

        self.sunday_mail = SundayMailFactory()
        self.sunday_mail_class = self.sunday_mail.get_mail_class()
        self.sunday_mail_prize = Mail.objects.get(id=MILESTONES[3]['mail_id'])

        self.sunday_mail_no_prize = SundayMailFactory(version=Mail.SUNDAY_NO_REFERRALS_PRIZE_VERSION)
        self.sunday_mail_no_prize_class = self.sunday_mail_no_prize.get_mail_class()

        self.regular_mail_sender_email = (
            '☕ El Tinto <info@eltinto.xyz>'
            if os.getenv('DJANGO_CONFIGURATION') == 'Production'
            else '☕ El Tinto Pruebas <info@dev.eltinto.xyz>'
        )

        self.milestone_mail = Mail.objects.get(id=MILESTONES[1]['mail_id'])
        self.milestone_mail_class = self.milestone_mail.get_mail_class()

        self.onboarding_mail = Mail.objects.get(id=UTILITY_MAILS[ONBOARDING_EMAIL_NAME])
        self.onboarding_mail_class = self.onboarding_mail.get_mail_class()

        self.change_preferred_days_mail = Mail.objects.get(id=UTILITY_MAILS[CHANGE_PREFERRED_DAYS])
        self.change_preferred_days_mail_class = self.change_preferred_days_mail.get_mail_class()

    def test_daily_mail_properties(self):
        daily_mail_headers = get_mail_headers(self.daily_mail)

        self.assertEqual(self.daily_mail_class.mail, self.daily_mail)
        self.assertEqual(self.daily_mail_class.mail_week_day, self.daily_mail.dispatch_date.weekday())
        self.assertEqual(self.daily_mail_class.template.template.origin, get_template('daily_mail').template.origin)
        self.assertEqual(self.daily_mail_class.headers, daily_mail_headers)
        self.assertEqual(self.daily_mail_class.sender_email, self.regular_mail_sender_email)

        user = UserFactory()

        # Test mail template data
        template_data = self.daily_mail_class.get_mail_template_data(user)

        daily_mail_template_keys = [
            'html', 'date', 'name', 'social_media_date', 'tweet', 'subject_message', 'referred_users_count',
            'referral_code', 'mail_version', 'env', 'uuid', 'mail_id', 'days_reminder'
        ]

        self.assertCountEqual(daily_mail_template_keys, template_data.keys())

        self.assertEqual(template_data['html'], self.daily_mail.html)
        self.assertEqual(template_data['date'], get_string_date(self.daily_mail.dispatch_date.date()))
        self.assertEqual(template_data['name'], user.user_name)
        self.assertEqual(template_data['social_media_date'], self.daily_mail.dispatch_date.date().strftime("%d-%m-%Y"))
        self.assertEqual(template_data['tweet'], urllib.parse.quote(self.daily_mail.tweet))
        self.assertEqual(template_data['subject_message'], self.daily_mail.subject_message)
        self.assertEqual(template_data['referred_users_count'], user.referred_users_count)
        self.assertEqual(template_data['referral_code'], user.referral_code)
        self.assertTrue(template_data['mail_version'])
        self.assertEqual(template_data['env'], get_env_value())
        self.assertEqual(template_data['uuid'], user.uuid)
        self.assertEqual(template_data['mail_id'], self.daily_mail.id)
        self.assertEqual(template_data['days_reminder'], False)

    def test_daily_mail_dispatch_users(self):
        valid_users, specific_dispatch_time_users = self._create_daily_mail_users()

        self.assertEqual(self.daily_mail_class.get_dispatch_users().count(), len(valid_users))
        self.assertEqual(
            self.daily_mail_class.get_dispatch_users(dispatch_time=time(7, 0)).count(),
            len(specific_dispatch_time_users)
        )

    def test_send_daily_mail(self):
        valid_users, _ = self._create_daily_mail_users()

        self.daily_mail_class.send_several_mails()

        self.assertEqual(len(mail.outbox), len(valid_users))

        first_mail = mail.outbox[0]

        mail_data = self.daily_mail_class.get_mail_template_data(valid_users[0])

        html = get_template('daily_mail').render(mail_data)

        self.assertEqual(first_mail.subject, self.daily_mail.subject)
        self.assertEqual(first_mail.body, html)
        self.assertEqual(first_mail.extra_headers, get_mail_headers(self.daily_mail))
        self.assertEqual(first_mail.from_email, self.regular_mail_sender_email)
        self.assertEqual(first_mail.reply_to, ['info@eltinto.xyz'])

    def test_sunday_mail_properties(self):

        self.assertEqual(self.sunday_mail_class.mail, self.sunday_mail)
        self.assertEqual(self.sunday_mail_class.mail_week_day, self.sunday_mail.dispatch_date.weekday())
        self.assertEqual(self.sunday_mail_class.template.template.origin, get_template('sunday_mail').template.origin)
        self.assertEqual(self.sunday_mail_class.headers, get_mail_headers(self.sunday_mail))
        self.assertEqual(self.sunday_mail_class.sender_email, self.regular_mail_sender_email)

        user = UserFactory()

        # Test mail template data
        template_data = self.sunday_mail_class.get_mail_template_data(user)

        sunday_mail_template_keys = [
            'html', 'date', 'name', 'social_media_date', 'tweet', 'subject_message', 'referred_users_count',
            'referral_code', 'mail_version', 'env', 'uuid', 'mail_id', 'has_sunday_mails_prize', 'missing_sunday_mails'
        ]

        self.assertCountEqual(sunday_mail_template_keys, template_data.keys())

        self.assertEqual(template_data['html'], self.sunday_mail.html)
        self.assertEqual(template_data['date'], get_string_date(self.sunday_mail.dispatch_date.date()))
        self.assertEqual(template_data['name'], user.user_name)
        self.assertEqual(template_data['social_media_date'], self.sunday_mail.dispatch_date.date().strftime("%d-%m-%Y"))
        self.assertEqual(template_data['tweet'], urllib.parse.quote(self.sunday_mail.tweet))
        self.assertEqual(template_data['subject_message'], self.sunday_mail.subject_message)
        self.assertEqual(template_data['referred_users_count'], user.referred_users_count)
        self.assertEqual(template_data['referral_code'], user.referral_code)
        self.assertTrue(template_data['mail_version'])
        self.assertEqual(template_data['env'], get_env_value())
        self.assertEqual(template_data['uuid'], user.uuid)
        self.assertEqual(template_data['mail_id'], self.sunday_mail.id)
        self.assertEqual(template_data['missing_sunday_mails'], user.missing_sunday_mails)
        self.assertEqual(template_data['has_sunday_mails_prize'], user.has_sunday_mails_prize)

    def test_sunday_mail_dispatch_users(self):
        valid_users, specific_dispatch_time_users = self._create_sunday_mail_users()

        self.assertEqual(self.sunday_mail_class.get_dispatch_users().count(), len(valid_users))
        self.assertEqual(
            self.sunday_mail_class.get_dispatch_users(dispatch_time=time(9, 0)).count(),
            len(specific_dispatch_time_users)
        )

    def test_send_sunday_mail(self):
        valid_users, _ = self._create_sunday_mail_users()

        self.sunday_mail_class.send_several_mails()

        self.assertEqual(len(mail.outbox), len(valid_users))

        first_mail = mail.outbox[0]

        mail_data = self.sunday_mail_class.get_mail_template_data(valid_users[0])

        html = get_template('sunday_mail').render(mail_data)

        self.assertEqual(first_mail.subject, self.sunday_mail.subject)
        self.assertEqual(first_mail.body, html)
        self.assertEqual(first_mail.extra_headers, get_mail_headers(self.sunday_mail))
        self.assertEqual(first_mail.from_email, self.regular_mail_sender_email)
        self.assertEqual(first_mail.reply_to, ['info@eltinto.xyz'])

    def test_sunday_no_prize_mail_properties(self):

        self.assertEqual(self.sunday_mail_no_prize_class.mail, self.sunday_mail_no_prize)
        self.assertEqual(self.sunday_mail_no_prize_class.mail_week_day,
                         self.sunday_mail_no_prize.dispatch_date.weekday())
        self.assertEqual(self.sunday_mail_class.template.template.origin, get_template('sunday_mail').template.origin)
        self.assertEqual(self.sunday_mail_no_prize_class.headers, get_mail_headers(self.sunday_mail_no_prize))
        self.assertEqual(self.sunday_mail_no_prize_class.sender_email, self.regular_mail_sender_email)

        user = UserFactory()

        # Test mail template data
        template_data = self.sunday_mail_class.get_mail_template_data(user)

        sunday_mail_template_keys = [
            'html', 'date', 'name', 'social_media_date', 'tweet', 'subject_message', 'referred_users_count',
            'referral_code', 'mail_version', 'env', 'uuid', 'mail_id', 'has_sunday_mails_prize', 'missing_sunday_mails'
        ]

        self.assertCountEqual(sunday_mail_template_keys, template_data.keys())

        self.assertEqual(template_data['html'], self.sunday_mail.html)
        self.assertEqual(template_data['date'], get_string_date(self.sunday_mail.dispatch_date.date()))
        self.assertEqual(template_data['name'], user.user_name)
        self.assertEqual(template_data['social_media_date'], self.sunday_mail.dispatch_date.date().strftime("%d-%m-%Y"))
        self.assertEqual(template_data['tweet'], urllib.parse.quote(self.sunday_mail.tweet))
        self.assertEqual(template_data['subject_message'], self.sunday_mail.subject_message)
        self.assertEqual(template_data['referred_users_count'], user.referred_users_count)
        self.assertEqual(template_data['referral_code'], user.referral_code)
        self.assertTrue(template_data['mail_version'])
        self.assertEqual(template_data['env'], get_env_value())
        self.assertEqual(template_data['uuid'], user.uuid)
        self.assertEqual(template_data['mail_id'], self.sunday_mail.id)
        self.assertEqual(template_data['missing_sunday_mails'], user.missing_sunday_mails)
        self.assertEqual(template_data['has_sunday_mails_prize'], user.has_sunday_mails_prize)

    def test_sunday_no_prize_mail_dispatch_users(self):
        users_with_no_prize = UserFactory.create_batch(size=5, missing_sunday_mails=0)

        # Users with prize
        users_with_prize = UserFactory.create_batch(size=5, missing_sunday_mails=0)

        for user_with_prize in users_with_prize:
            SentEmailsFactory(user=user_with_prize, mail=self.sunday_mail_prize)

        # Users with missing sunday mails
        UserFactory.create_batch(size=5, missing_sunday_mails=1)

        # Users with day not selected
        UserFactory.create_batch(size=5, preferred_email_days=[1, 2, 4], missing_sunday_mails=0)

        # Users who already received mail
        users_already_receive_mail = UserFactory.create_batch(size=5, missing_sunday_mails=0)

        for user_already_receive_mail in users_already_receive_mail:
            SentEmailsFactory(user=user_already_receive_mail, mail=self.sunday_mail_no_prize)

        self.assertEqual(
            self.sunday_mail_no_prize_class.get_dispatch_users().count(),
            len(users_with_no_prize)
        )

    def test_milestone_mail_properties(self):
        milestone_sender_email = (
            '☕ El Tinto - CEO <alejandro@eltinto.xyz>'
            if os.getenv('DJANGO_CONFIGURATION') == 'Production'
            else '☕ El Tinto Pruebas - CEO <alejandro@dev.eltinto.xyz>'
        )

        self.assertEqual(self.milestone_mail_class.mail, self.milestone_mail)
        self.assertEqual(self.milestone_mail_class.template.template.origin, get_template('milestones').template.origin)
        self.assertEqual(self.milestone_mail_class.headers, get_mail_headers(self.milestone_mail))
        self.assertEqual(self.milestone_mail_class.sender_email, milestone_sender_email)

        user = UserFactory()

        # Test mail template data
        template_data = self.milestone_mail_class.get_mail_template_data(user)

        milestone_mail_template_keys = ['html']

        self.assertCountEqual(milestone_mail_template_keys, template_data.keys())

        self.assertEqual(template_data['html'], replace_words_in_sentence(self.milestone_mail.html, user=user))

    def test_onboarding_mail_properties(self):

        self.assertEqual(self.onboarding_mail_class.mail, self.onboarding_mail)
        self.assertEqual(
            self.onboarding_mail_class.template.template.origin, get_template('onboarding').template.origin
        )
        self.assertEqual(self.onboarding_mail_class.headers, get_mail_headers(self.onboarding_mail))
        self.assertEqual(self.onboarding_mail_class.sender_email, self.regular_mail_sender_email)

        user = UserFactory()

        # Test mail template data
        template_data = self.onboarding_mail_class.get_mail_template_data(user)

        sunday_mail_template_keys = ['html']

        self.assertCountEqual(sunday_mail_template_keys, template_data.keys())

        self.assertEqual(template_data['html'], replace_words_in_sentence(self.onboarding_mail.html, user=user))

    def test_change_preferred_days_mail_properties(self):

        self.assertEqual(self.change_preferred_days_mail_class.mail, self.change_preferred_days_mail)
        self.assertEqual(
            self.change_preferred_days_mail_class.template.template.origin,
            get_template('change_preferred_days').template.origin
        )
        self.assertEqual(
            self.change_preferred_days_mail_class.headers, get_mail_headers(self.change_preferred_days_mail)
        )
        self.assertEqual(self.change_preferred_days_mail_class.sender_email, self.regular_mail_sender_email)

        user = UserFactory()

        # Test mail template data
        template_data = self.change_preferred_days_mail_class.get_mail_template_data(user)

        change_preferred_days_mail_keys = ['html']

        self.assertCountEqual(change_preferred_days_mail_keys, template_data.keys())

        self.assertEqual(template_data['html'],
                         replace_words_in_sentence(self.change_preferred_days_mail.html, user=user))

    def _create_daily_mail_users(self):
        regular_users = UserFactory.create_batch(size=5)
        dispatch_day_preferred_days_users = UserFactory.create_batch(
            size=5,
            preferred_email_days=[self.daily_mail.dispatch_date.weekday()]
        )

        # Users with day not selected
        UserFactory.create_batch(
            size=5,
            preferred_email_days=[(self.daily_mail.dispatch_date + timedelta(days=1)).weekday()]
        )

        # Users who already received mail
        users_already_receive_mail = UserFactory.create_batch(size=5, missing_sunday_mails=0)

        for user_already_receive_mail in users_already_receive_mail:
            SentEmailsFactory(user=user_already_receive_mail, mail=self.daily_mail)

        # Users with specific dispatch time
        dispatch_time = time(7, 0)
        specific_dispatch_time_users = UserFactory.create_batch(size=5, dispatch_time=dispatch_time)

        return regular_users + dispatch_day_preferred_days_users, specific_dispatch_time_users

    def _create_sunday_mail_users(self):
        users_with_missing_sunday_mails = UserFactory.create_batch(size=5, missing_sunday_mails=1)

        users_with_prize = UserFactory.create_batch(size=5)

        for user_with_prize in users_with_prize:
            SentEmailsFactory(user=user_with_prize, mail=self.sunday_mail_prize)

        # Users with specific dispatch time
        dispatch_time = time(9, 0)
        specific_dispatch_time_users = UserFactory.create_batch(
            size=5, missing_sunday_mails=1, dispatch_time=dispatch_time
        )

        # Users with day not selected
        UserFactory.create_batch(size=5, preferred_email_days=[1, 2, 4])

        # Users with no prize
        UserFactory.create_batch(size=5, missing_sunday_mails=0)

        # Users who already received mail
        users_already_receive_mail = UserFactory.create_batch(size=5, missing_sunday_mails=0)

        for user_already_receive_mail in users_already_receive_mail:
            SentEmailsFactory(user=user_already_receive_mail, mail=self.sunday_mail)

        # Old sunday emails sent to test uniqueness of ids
        sunday_mails = SundayMailFactory.create_batch(size=5)

        for sunday_mail in sunday_mails:
            for user in users_with_prize:
                SentEmailsFactory(user=user, mail=sunday_mail)

        return users_with_missing_sunday_mails + users_with_prize, specific_dispatch_time_users
