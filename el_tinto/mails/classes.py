import logging
import os
import random
import urllib.parse
from datetime import datetime

from django.core.mail import EmailMessage
from django.db.models import Q
from django.template import loader
from django.utils.safestring import mark_safe

from el_tinto.users.models import User
from el_tinto.utils.date_time import get_string_date
from el_tinto.utils.utils import replace_words_in_sentence, get_env_value, MILESTONES, \
    TASTE_CLUB_TIER_COFFEE_BEAN_WELCOME_MAIL_ID, TASTE_CLUB_TIER_GROUND_COFFEE_WELCOME_MAIL_ID, \
    TASTE_CLUB_TIER_TINTO_WELCOME_MAIL_ID, TASTE_CLUB_TIER_EXPORTATION_COFFEE_WELCOME_MAIL_ID

logger = logging.getLogger("mails")


class Mail:

    def __init__(self, mail):
        self.mail = mail
        self.mail_week_day = self.mail.dispatch_date.weekday()
        self.template = self.set_template()
        self.headers = self.set_headers()
        self.sender_email = self.set_sender_email()

    def get_dispatch_users(self):
        """
        Get dispatch users list.
        """
        pass

    def get_mail_template_data(self, user=None):
        """
        Get mail template data.

        params:
        user: User obj

        return:
        mail_template_data = dict
        """
        mail_data = {
            'html': mark_safe(replace_words_in_sentence(self.mail.html, user=user)),
            'mail_version': True,
            'user_name': user.user_name if user else ''
        }

        return mail_data

    def set_template(self):
        """
        Set mail template.
        """
        return loader.get_template('../templates/mailings/default.html')

    def set_sender_email(self):
        """
        Set sending mail address.
        """
        return (
            '☕ El Tinto <info@eltinto.xyz>'
            if os.getenv('DJANGO_CONFIGURATION') == 'Production'
            else '☕ El Tinto Pruebas <info@dev.eltinto.xyz>'
        )

    def set_headers(self):
        """
        Set mail headers.
        """
        return {
            'X-SES-CONFIGURATION-SET': (
                'Engagement'
                if os.getenv('DJANGO_CONFIGURATION') == 'Production'
                else 'Engagement_dev'
            ),
            'EMAIL-ID': str(self.mail.id),
            'EMAIL-TYPE': self.mail.type
        }

    def send_mail(self, user=None, mail_address=None, extra_data=None, test=False):
        """
        Send mail.
        """
        mail_data = self.get_mail_template_data(user)

        if extra_data:
            mail_data.update(extra_data)

        html = self.template.render(mail_data)

        message_user = EmailMessage(
            replace_words_in_sentence(self.mail.subject, user=user),
            html,
            self.sender_email,
            [user.email if user else mail_address],
            reply_to=['info@eltinto.xyz'],
            headers=self.headers
        )

        message_user.content_subtype = 'html'
        message_user.send(fail_silently=True)

        if not test:
            self.mail.recipients.add(user)

    def send_mail_batch(self, users_batch):
        """
        Send mails batch.

        params:
        users_batch: [User obj]
        """
        for user in users_batch:
            self.send_mail(user)

    def send_several_mails(self, dispatch_time=None):
        """
        Send several mails.

        params:
        dispatch_time: time
        """
        users = self.get_dispatch_users(dispatch_time)

        # This number is based on AWS SES limitations.
        # Is calculated based on the average sending time per email and the maximum number of mails/s - 1
        # to make sure never surpass AWS email sending capability
        n = 200

        # Split total users into chunks of length n to send at most those emails per second
        users_chunked_list = [users[i:i + n] for i in range(0, len(users), n)]

        for users_bach in users_chunked_list:
            self.send_mail_batch(users_bach)

        self.mail.sent_datetime = datetime.now()
        self.mail.save()


class DailyMail(Mail):

    def get_dispatch_users(self, dispatch_time=None):
        """
        Get dispatch users list.

        params:
        dispatch_time: time
        """
        return User.objects.filter(
            (Q(preferred_email_days__contains=[self.mail_week_day]) | Q(preferred_email_days__len=0)),
            is_active=True,
            dispatch_time=dispatch_time
        ).exclude(sentemails__mail_id=self.mail.id).distinct()

    def get_mail_template_data(self, user=None):
        """
        Get mail template data.

        params:
        user: User obj

        return:
        mail_template_data = dict
        """
        mail_data = {
            'html': mark_safe(replace_words_in_sentence(self.mail.html, user=user)),
            'date': get_string_date(self.mail.dispatch_date.date()),
            'name': user.user_name if user else '',
            'social_media_date': self.mail.dispatch_date.date().strftime("%d-%m-%Y"),
            'tweet': urllib.parse.quote(self.mail.tweet),
            'subject_message': self.mail.subject_message,
            'referred_users_count': user.referred_users_count if user else 0,
            'referral_code': user.referral_code if user else '',
            'mail_version': True if user else False,
            'env': get_env_value(),
            'uuid': user.uuid if user else '',
            'mail_id': self.mail.id,
            'days_reminder': True if user and 0 < len(user.preferred_email_days) < 7 else False,
            'user_tier': True if user and user.tiers.filter(valid_to__gte=datetime.today()).exists() else False
        }

        return mail_data

    def set_template(self):
        """
        Set mail template.
        """
        return loader.get_template('../templates/mailings/daily_mail.html')


class SundayMail(Mail):

    def get_dispatch_users(self, dispatch_time=None):
        """
        Get dispatch users list.
        """
        return User.objects.filter(
            # Filter day selected
            (Q(preferred_email_days__contains=[self.mail_week_day]) | Q(preferred_email_days__len=0)),
            # Filter missing sunday emails
            Q(missing_sunday_mails__gt=0) |
            # Filter has prize
            Q(sentemails__mail_id=MILESTONES[3]['mail_id']),
            is_active=True,
            dispatch_time=dispatch_time
        ).exclude(sentemails__mail_id=self.mail.id).distinct()

    def get_mail_template_data(self, user):
        """
        Get mail template data.

        params:
        user: User obj

        return:
        mail_template_data = dict
        """
        mail_data = {
            'html': mark_safe(replace_words_in_sentence(self.mail.html, user=user)),
            'date': get_string_date(self.mail.dispatch_date.date()),
            'name': user.user_name,
            'social_media_date': self.mail.dispatch_date.date().strftime("%d-%m-%Y"),
            'tweet': urllib.parse.quote(self.mail.tweet),
            'subject_message': self.mail.subject_message,
            'referred_users_count': user.referred_users_count,
            'referral_code': user.referral_code,
            'mail_version': True,
            'env': get_env_value(),
            'uuid': user.uuid,
            'missing_sunday_mails': user.missing_sunday_mails,
            'has_sunday_mails_prize': user.has_sunday_mails_prize,
            'mail_id': self.mail.id,
            'user_tier': True if user.tiers.filter(valid_to__gte=datetime.today()).exists() else False
        }

        return mail_data

    def set_template(self):
        """
        Set mail template.
        """
        return loader.get_template('../templates/mailings/sunday_mail.html')


class SundayNoPrizeMail(Mail):

    def get_dispatch_users(self, dispatch_time=None):
        """
        Get dispatch users list.
        """
        return User.objects.filter(
            # Filter day selected
            (Q(preferred_email_days__contains=[self.mail_week_day]) | Q(preferred_email_days__len=0)),
            # Filter missing sunday emails
            missing_sunday_mails=0,
            is_active=True
        ).exclude(sentemails__mail_id__in=[self.mail.id, MILESTONES[3]['mail_id']]).distinct()

    def get_mail_template_data(self, user):
        """
        Get mail template data.

        params:
        user: User obj

        return:
        mail_template_data = dict
        """
        mail_data = {
            'html': mark_safe(replace_words_in_sentence(self.mail.html, user=user)),
            'date': get_string_date(self.mail.dispatch_date.date()),
            'name': user.user_name,
            'social_media_date': self.mail.dispatch_date.date().strftime("%d-%m-%Y"),
            'email': user.email,
            'tweet': urllib.parse.quote(self.mail.tweet),
            'subject_message': self.mail.subject_message,
            'referred_users_count': user.referred_users_count,
            'referral_code': user.referral_code,
            'mail_version': True,
            'env': get_env_value(),
            'uuid': user.uuid,
            'missing_sunday_mails': user.missing_sunday_mails,
            'has_sunday_mails_prize': user.has_sunday_mails_prize,
            'mail_id': self.mail.id
        }

        return mail_data

    def set_template(self):
        """
        Set mail template.
        """
        return loader.get_template('../templates/mailings/sunday_mail.html')

    def send_mail_batch(self, users_batch):
        """
        Send mails batch based on user's open rate.

        params:
        users_batch: [User obj]
        """
        for user in users_batch:
            if random.random() < user.open_rate:
                self.send_mail(user)


class MilestoneMail(Mail):

    def set_template(self, user=None):
        """
        Set mail template.
        """
        return loader.get_template('../templates/mailings/milestones.html')

    def set_sender_email(self):
        """
        Set sending mail address.
        """
        return (
            '☕ El Tinto - CEO <alejandro@eltinto.xyz>'
            if os.getenv('DJANGO_CONFIGURATION') == 'Production'
            else '☕ El Tinto Pruebas - CEO <alejandro@dev.eltinto.xyz>'
        )


class OnboardingMail(Mail):

    def set_template(self, user=None):
        """
        Set mail template.
        """
        return loader.get_template('../templates/mailings/onboarding.html')


class ChangePreferredDaysMail(Mail):

    def set_template(self):
        """
        Set mail template.
        """
        return loader.get_template('../templates/mailings/change_preferred_days.html')


class TasteClubMail(Mail):

    def set_sender_email(self):
        """
        Set sending mail address.
        """
        if os.getenv('DJANGO_CONFIGURATION') == 'Production':
            return (
                '☕ El Tinto - CEO <alejandro@eltinto.xyz>'
                if self.mail.id in [
                    TASTE_CLUB_TIER_COFFEE_BEAN_WELCOME_MAIL_ID,
                    TASTE_CLUB_TIER_GROUND_COFFEE_WELCOME_MAIL_ID,
                    TASTE_CLUB_TIER_TINTO_WELCOME_MAIL_ID,
                    TASTE_CLUB_TIER_EXPORTATION_COFFEE_WELCOME_MAIL_ID
                ]
                else '☕ El Tinto <info@eltinto.xyz>'
            )

        else:
            return (
                '☕ El Tinto Pruebas - CEO <alejandro@dev.eltinto.xyz>'
                if self.mail.id in [
                    TASTE_CLUB_TIER_COFFEE_BEAN_WELCOME_MAIL_ID,
                    TASTE_CLUB_TIER_GROUND_COFFEE_WELCOME_MAIL_ID,
                    TASTE_CLUB_TIER_TINTO_WELCOME_MAIL_ID,
                    TASTE_CLUB_TIER_EXPORTATION_COFFEE_WELCOME_MAIL_ID
                ]
                else '☕ El Tinto Pruebas <info@dev.eltinto.xyz>'
            )

    def set_template(self):
        """
        Set mail template.
        """
        return loader.get_template('../templates/mailings/survey.html')
