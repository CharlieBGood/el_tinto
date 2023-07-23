import logging
import os

from django.core.mail import EmailMessage
from django.db.models import Q
from django.template import loader
from django.utils.safestring import mark_safe

from el_tinto.users.models import User
from el_tinto.utils.date_time import get_string_date
from el_tinto.utils.utils import replace_words_in_sentence, replace_special_characters_for_url_use, get_env_value, \
    MILESTONES

logger = logging.getLogger("mails")


class Mail:

    def __init__(self, mail):
        self.mail = mail
        self.mail_week_day = self.mail.dispatch_date.date().weekday()
        self.template = None
        self.reply_to = None
        self.headers = None
        self.sender_email = ''

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

    def send_mail(self, user=None, mail_address=None, extra_data=None):
        """
        Send mail.
        """
        self.set_template()
        self.set_sender_email()

        mail_data = self.get_mail_template_data()

        if extra_data:
            mail_data.update(extra_data)

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

        self.mail.recipients.add(user)

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

    def get_dispatch_users(self):
        """
        Get dispatch users list.
        """
        return User.objects.filter(
            (Q(preferred_email_days__contains=[self.mail_week_day]) | Q(preferred_email_days__len=0)),
            sentemails__mail_id=self.mail.id,
            sentemails__isnull=True,
            is_active=True
        ).distinct()

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

    def get_dispatch_users(self):
        """
        Get dispatch users list.
        """
        return User.objects.filter(
            # Filter day selected
            (Q(preferred_email_days__contains=[self.mail_week_day]) | Q(preferred_email_days__len=0)),
            # Filter mail not sent previously
            (Q(sentemails__mail_id__in=self.mail.id), Q(sentemails__isnull=True)),
            # Filter missing sunday emails
            Q(
                missing_sunday_mails__gt=0
            ) |
            # Filter has prize
            (Q(sentemails__mail_id__in=MILESTONES[3]['mail_id']), Q(sentemails__isnull=False)),
            is_active=True
        ).distinct()

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

    def set_template(self, user):
        """
        Set mail template.
        """
        template_name = 'sunday_mail.html'

        self.template = loader.get_template(f'../templates/mailings/{template_name}')


class SundayNoPrizeMail(Mail):

    def get_dispatch_users(self):
        """
        Get dispatch users list.
        """
        return User.objects.filter(
            # Filter day selected
            (Q(preferred_email_days__contains=[self.mail_week_day]) | Q(preferred_email_days__len=0)),
            # Filter mail not sent previously
            (Q(sentemails__mail_id__in=self.mail.id), Q(sentemails__isnull=True)),
            # Filter missing sunday emails
            Q(
                missing_sunday_mails=0
            ) |
            # Filter has prize
            (Q(sentemails__mail_id__in=MILESTONES[3]['mail_id']), Q(sentemails__isnull=True)),
            is_active=True
        ).distinct()

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

    def set_template(self, user):
        """
        Set mail template.
        """
        template_name = 'sunday_mail.html'

        self.template = loader.get_template(f'../templates/mailings/{template_name}')


class MilestoneMail(Mail):

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
            'mail_id': self.mail.id
        }

        return mail_data

    def set_template(self, user=None):
        """
        Set mail template.
        """
        template_name = 'milestones.html'

        self.template = loader.get_template(f'../templates/mailings/{template_name}')

    def set_sender_email(self):
        """
        Set sending mail address.
        """
        self.sender_email = (
            '☕ El Tinto - CEO <alejandro@eltinto.xyz>'
            if os.getenv('DJANGO_CONFIGURATION') == 'Production'
            else '☕ El Tinto Pruebas - CEO <alejandro@dev.eltinto.xyz>'
        )


class OnboardingMail(Mail):

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
            'mail_id': self.mail.id
        }

        return mail_data

    def set_template(self, user=None):
        """
        Set mail template.
        """
        template_name = 'onboarding.html'

        self.template = loader.get_template(f'../templates/mailings/{template_name}')


class ChangePreferredDaysMail(Mail):

    #TODO: Review
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
            'mail_id': self.mail.id
        }

        return mail_data

    def set_template(self, user=None):
        """
        Set mail template.
        """
        template_name = 'change_preferred_days.html'

        self.template = loader.get_template(f'../templates/mailings/{template_name}')