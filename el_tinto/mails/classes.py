import logging
import os
from datetime import datetime, timezone

from django.core.mail import EmailMessage
from django.template import loader
from django.utils.safestring import mark_safe

from el_tinto.users.models import User
from el_tinto.utils.date_time import get_string_date, convert_utc_to_local_datetime
from el_tinto.utils.utils import replace_words_in_sentence, replace_special_characters_for_url_use, get_env_value


logger = logging.getLogger("mails")


class Mail:

    def __init__(self, mail):
        self.mail = mail
        self.mail_week_day = convert_utc_to_local_datetime(timezone.now()).date().weekday()
        self.template = None
        self.reply_to = None
        self.headers = None
        self.sender_email = ''

    def get_dispatch_users(self):
        """
        Get dispatch users list.
        """
        users = User.objects.filter(is_active=True)

        return [user for user in users if self.send_mail_to_user(user)]

    def send_mail_to_user(self, user):
        """
        Define whether the email should be sent to the user or not.

        params:
        user: User obj
        """
        return True

    def get_mail_template_data(self, user=None):
        """
        Get mail template data.

        params:
        user: User obj

        return:
        mail_template_data = dict
        """
        pass

    def set_template(self, user=None):
        """
        Set mail template.
        """
        self.template = loader.get_template(f'../templates/mailings/default.html')

    def set_sender_email(self):
        """
        Set sending mail address.
        """
        self.sender_email = (
            '☕ El Tinto <info@eltinto.xyz>'
            if os.getenv('DJANGO_CONFIGURATION') == 'Production'
            else '☕ El Tinto Pruebas <info@dev.eltinto.xyz>'
        )

    def set_headers(self):
        """
        Set mail headers.
        """
        self.headers = {
            'X-SES-CONFIGURATION-SET': (
                'Engagement'
                if os.getenv('DJANGO_CONFIGURATION') == 'Production'
                else 'Engagement_dev'
            ),
            'EMAIL-ID': str(self.mail.id),
            'EMAIL-TYPE': self.mail.type
        }

    def is_weekday_selected_by_user(self, user):
        """
        Define if the current week day is selected by the user
        """
        return (self.week_day in user.preferred_email_days) or (len(user.preferred_email_days) == 0)

    def has_mail_already_been_sent_to_user(self, user):
        """
        Defines if the mail has already been sent to the user.
        """
        return self.mail.sentemails_set.filter(user=user).exists()

    def send_mail(self, user=None, mail_address=None):
        """
        Send mail.
        """
        self.set_template()
        self.set_sender_email()

        mail_data = self.get_mail_template_data()

        html = self.template.render(mail_data)

        message_user = EmailMessage(
            replace_words_in_sentence(self.mail.subject, user=user),
            html,
            self.sender_email,
            user.email if user else mail_address,
            reply_to=[self.reply_to] if self.reply_to else ['info@eltinto.xyz'],
            headers=self.headers
        )

        message_user.content_subtype = 'html'
        message_user.send(fail_silently=True)

    def send_mail_batch(self, users_batch):
        """
        Send mails batch.

        params:
        users_batch: [User obj]
        """
        for user in users_batch:
            self.send_mail(user)

    def send_several_mails(self):
        """
        Send several mails.
        """
        users = self.get_dispatch_users()

        # This number is based on AWS SES limitations.
        # Is calculated based on the average sending time per email and the maximum number of mails/s - 1
        # to make sure never surpass AWS email sending capability
        n = 200

        # Split total users into chunks of length n to send at most those emails per second
        users_chunked_list = [users[i:i + n] for i in range(0, len(users), n)]

        for users_bach in users_chunked_list:
            self.send_mail_batch(users_bach)


class DailyMail(Mail):

    def send_mail_to_user(self, user):
        """
        Define whether the email should be sent to the user or not.

        params:
        user: User obj
        """
        is_weekday_selected_by_user = self.is_weekday_selected_by_user(user)
        has_mail_already_been_sent_to_user = self.has_mail_already_been_sent_to_user(user)

        return is_weekday_selected_by_user and not has_mail_already_been_sent_to_user

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
            'name': user.user_name if user else '',
            'social_media_date': self.mail.dispatch_date.date().strftime("%d-%m-%Y"),
            'tweet': replace_special_characters_for_url_use(self.mail.tweet),
            'subject_message': self.mail.subject_message,
            'referred_users_count': user.referred_users_count if user else 0,
            'referral_code': user.referral_code if user else '',
            'mail_version': True,
            'env': get_env_value(),
            'uuid': user.uuid if user else '',
            'mail_id': self.mail.id
        }

        return mail_data

    def set_template(self, user):
        """
        Set mail template.
        """
        template_name = 'daily_mail_with_days.html' if 0 < len(user.preferred_email_days) < 7 else 'daily_mail.html'

        self.template = loader.get_template(f'../templates/mailings/{template_name}')


class SundayMail(Mail):

    def send_mail_to_user(self, user):
        """
        Define whether the email should be sent to the user or not.

        params:
        user: User obj
        """
        has_sunday_mails_prize = user.has_sunday_mails_prize
        is_weekday_selected_by_user = self.is_weekday_selected_by_user(user)
        has_mail_already_been_sent_to_user = self.has_mail_already_been_sent_to_user(user)

        return has_sunday_mails_prize and is_weekday_selected_by_user and not has_mail_already_been_sent_to_user

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
            'name': user.user_name if user else '',
            'social_media_date': self.mail.dispatch_date.date().strftime("%d-%m-%Y"),
            'email': user.email if user else '',
            'tweet': replace_special_characters_for_url_use(self.mail.tweet),
            'subject_message': self.mail.subject_message,
            'referred_users_count': user.referred_users_count if user else 0,
            'referral_code': user.referral_code if user else '',
            'mail_version': True,
            'env': get_env_value(),
            'uuid': user.uuid if user else '',
            'missing_sunday_mails': user.missing_sunday_mails if user else 0,
            'has_sunday_mails_prize': user.has_sunday_mails_prize if user else True,
            'mail_id': self.mail.id
        }

        return mail_data
