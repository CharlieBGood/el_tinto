import uuid
from datetime import datetime

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.postgres.fields import ArrayField
from phonenumber_field.modelfields import PhoneNumberField

from el_tinto.users.managers import UserManager


class User(AbstractUser):
    objects = UserManager()

    TWITTER = 'twitter'
    FACEBOOK = 'facebook'
    WHATSAPP = 'whatsapp'
    INSTAGRAM = 'instagram'

    UTM_SOURCE_TYPE_CHOICES = (
        (TWITTER, 'Twitter'),
        (FACEBOOK, 'Facebook'),
        (WHATSAPP, 'Whatsapp'),
        (INSTAGRAM, 'Instagram'),
    )

    email = models.EmailField(
        'email address',
        unique=True,
        blank=False,
        null=False,
        error_messages={
            'unique': 'A user with that email already exists.'
        }
    )

    phone_number = PhoneNumberField(blank=True)
    first_name = models.CharField(max_length=25, blank=True, default='')
    last_name = models.CharField(max_length=25, blank=True, default='')
    username = None
    preferred_email_days = ArrayField(models.SmallIntegerField(), blank=True, default=list)
    best_user = models.BooleanField(default=False)
    referral_code = models.CharField(max_length=6, blank=True, default='')
    uuid = models.UUIDField(default=uuid.uuid4, null=True)
    referred_by = models.ForeignKey(
        'users.User',
        default=None,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='referred_users'
    )

    dispatch_time = models.TimeField(default=None, null=True, blank=True)
    missing_sunday_mails = models.SmallIntegerField(default=4)
    utm_source = models.CharField(choices=UTM_SOURCE_TYPE_CHOICES, default='', blank=True, max_length=25)
    medium = models.CharField(default='', blank=True, max_length=25)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    @property
    def user_name(self):
        """
        returns the first name of the user if it exists else returns the email of the user.

        :return:
        user_name: str
        """
        return self.first_name if self.first_name and self.first_name != '' else self.email.split('@')[0]

    @property
    def opened_mails(self):
        """
        returns how many emails the user has opened

        :return:
        opened_mails: int
        """
        return self.sentemails_set.exclude(opened_date=None).count()

    @property
    def open_rate(self):
        """
        returns the open rate of the user.

        :return:
        open_rate: float
        """
        return self.opened_mails / (self.sentemails_set.count() or 1)

    @property
    def referred_users_count(self):
        """
        Calculate referred users invited by current user.
        Referred users are those who have been referred by someone and have opened at least
        one email. They can be active or inactive

        :return:
        referred_users_count: int
        """
        referred_users = User.objects.filter(referred_by=self)

        referred_users_count = 0

        for referred_user in referred_users:
            if referred_user.sentemails_set.exclude(opened_date=None).count() > 0:
                referred_users_count += 1

        return referred_users_count

    @property
    def has_sunday_mails_prize(self):
        """
        Check if the user has received the email with the prize of the sunday mails

        :return:
        has_sunday_mails_prize: bool
        """
        from el_tinto.utils.utils import MILESTONES

        return self.sentemails_set.filter(mail_id=MILESTONES[3]['mail_id']).exists()

    @property
    def recency(self):
        """
        Current time in days from the date the user joined.

        :return:
        recency: int
        """
        return (datetime.now().date() - self.date_joined.date()).days

    @property
    def current_tier(self):
        """
        Current tier.

        :return:
        user_tier: UserTier obj
        """
        user_tier = self.usertier_set.filter(valid_to__date__gte=datetime.now()).order_by('-valid_to').first()

        return user_tier

    @property
    def env(self):
        """
        Returns the environment on which the code is being executed.

        :return:
        env: str
        """
        from el_tinto.utils.utils import get_env_value

        return get_env_value()

    def __str__(self):
        return self.email


class Unsuscribe(models.Model):
    user = models.OneToOneField('users.User', on_delete=models.CASCADE)
    boring = models.BooleanField(default=False)
    invasive = models.BooleanField(default=False)
    variety = models.BooleanField(default=False)
    not_used = models.BooleanField(default=False)
    other_email = models.BooleanField(default=False)
    recommendation = models.TextField(default='', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    edited_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user}'


class UserVisits(models.Model):
    SUBSCRIBE_PAGE = 'SP'
    REFERRAL_HUB = 'RH'

    VISIT_TYPES = [
        (SUBSCRIBE_PAGE, 'Suscripción'),
        (REFERRAL_HUB, 'Centro de referidos'),
    ]
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    mail = models.ForeignKey('mails.Mail', on_delete=models.CASCADE, null=True, default=None)
    type = models.CharField(choices=VISIT_TYPES, max_length=4)
    created_at = models.DateTimeField(auto_now_add=True)


class UserButtonsInteractions(models.Model):
    TWITTER = 'TW'
    FACEBOOK = 'FB'
    WHATSAPP = 'WP'
    COPY_PASTE = 'CP'

    INTERACTION_TYPE = [
        (TWITTER, 'Twitter'),
        (FACEBOOK, 'Facebook'),
        (WHATSAPP, 'Whatsapp'),
        (COPY_PASTE, 'Copy & paste')
    ]

    visit = models.ForeignKey('users.UserVisits', on_delete=models.CASCADE)
    medium = models.CharField(default='', blank=True, max_length=25)
    type = models.CharField(max_length=4, choices=INTERACTION_TYPE)
    created_at = models.DateTimeField(auto_now_add=True)


class UserTier(models.Model):
    TIER_COFFEE_SEED = 1
    TIER_COFFEE_BEAN = 2
    TIER_TINTO = 3
    TIER_EXPORTATION_COFFEE = 4

    TIERS_CHOICES = (
        (TIER_COFFEE_SEED, 'Semilla de café'),
        (TIER_COFFEE_BEAN, 'Grano de café'),
        (TIER_TINTO, 'Tinto'),
        (TIER_EXPORTATION_COFFEE, 'Café de exportación')
    )

    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    payment = models.OneToOneField('stripe.StripePayment', on_delete=models.CASCADE)
    tier = models.SmallIntegerField(choices=TIERS_CHOICES)
    valid_from = models.DateTimeField(auto_now_add=True)
    valid_to = models.DateTimeField()
