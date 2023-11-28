import datetime

from django.conf import settings
from django.db import models
from django.template import loader
from django.template.exceptions import TemplateDoesNotExist
from tinymce.models import HTMLField

from el_tinto.mails.classes import DailyMail, SundayMail, SundayNoPrizeMail, MilestoneMail, OnboardingMail, \
    ChangePreferredDaysMail, TasteClubMail
from el_tinto.utils.date_time import get_string_date
from el_tinto.utils.utils import generate_random_alphanumeric_code


class Mail(models.Model):
    """Mail class."""

    # TODO add SQL field for personalized queries

    # Type constants
    DAILY = 'Daily'
    TEST = 'Test'
    PROMOTION = 'Promotion'
    WELCOME = 'Welcome'
    MILESTONE = 'Milestone'
    CHANGE_PREFERRED_DAYS = 'Preferred days'
    TASTE_CLUB = 'Taste club'
    SUNDAY = 'Sunday'

    TYPE_OPTIONS = [
        (DAILY, 'Diario'),
        (TEST, 'Testeo'),
        (PROMOTION, 'Promoción'),
        (WELCOME, 'Bienvenida'),
        (MILESTONE, 'Meta de referidos'),
        (CHANGE_PREFERRED_DAYS, 'Cambiar días preferidos'),
        (TASTE_CLUB, 'Club de Cata'),
        (SUNDAY, 'Dominguero')
    ]

    # Version constants
    A_VERSION = 'A'
    B_VERSION = 'B'
    SUNDAY_NO_REFERRALS_PRIZE_VERSION = 'SUNDAY NO PRIZE'
    DEFAULT_TESTING_VERSION = 'DEFAULT'

    VERSION_OPTIONS = [
        (A_VERSION, 'A'),
        (B_VERSION, 'B'),
        (SUNDAY_NO_REFERRALS_PRIZE_VERSION, 'Dominguero sin premios'),
        (DEFAULT_TESTING_VERSION, 'Testeo en blanco')
    ]

    html = HTMLField()
    subject = models.CharField(max_length=256, default='')
    type = models.CharField(
        max_length=15,
        choices=TYPE_OPTIONS,
    )
    test_email = models.EmailField(default='', blank=True)
    version = models.CharField(
        max_length=15,
        choices=VERSION_OPTIONS,
        default='A'
    )

    created_by = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        related_name='sent_emails',
        null=True,
        blank=True,
        editable=False
    )
    created_at = models.DateTimeField(auto_now_add=True)
    dispatch_date = models.DateTimeField(null=True, blank=False)
    programmed = models.BooleanField(default=False, editable=False)
    tinto = models.OneToOneField('tintos.Tinto', on_delete=models.SET_NULL, null=True, related_name='mail')
    sponsor_image_url = models.URLField(default='', blank=True)
    sponsor_image_url_width = models.IntegerField(null=True, blank=True)
    sponsor_web_url = models.URLField(default='', blank=True)
    tweet = models.CharField(max_length=256, default='', help_text='256 characters max')
    subject_message = models.CharField(max_length=256, default='', blank=True,
                                       help_text='Texto que acompaña al subject')

    sent_datetime = models.DateTimeField(default=None, blank=True, null=True)

    recipients = models.ManyToManyField(
        'users.User',
        related_name='received_emails',
        through="mails.SentEmails",
        through_fields=('mail', 'user'),
        blank=True
    )

    class Meta:
        verbose_name = "Mail"
        verbose_name_plural = "Mails"

    def __str__(self):
        return f'{self.type} - {self.created_at.strftime("%d-%m-%Y")}'

    def get_mail_class(self):
        """
        Get mail class based on mail type
        """

        MAIL_CLASS_MAPPER = {
            Mail.DAILY: DailyMail,
            Mail.SUNDAY: SundayMail,
            Mail.SUNDAY_NO_REFERRALS_PRIZE_VERSION: SundayNoPrizeMail,
            Mail.MILESTONE: MilestoneMail,
            Mail.WELCOME: OnboardingMail,
            Mail.CHANGE_PREFERRED_DAYS: ChangePreferredDaysMail,
            Mail.TASTE_CLUB: TasteClubMail
        }

        try:
            mail_class = MAIL_CLASS_MAPPER[self.version]

        except KeyError:
            mail_class = MAIL_CLASS_MAPPER[self.type]

        return mail_class(self)


class SentEmails(models.Model):
    mail = models.ForeignKey('mails.Mail', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    opened_date = models.DateTimeField(default=None, null=True)
    sns_object = models.OneToOneField('ses_sns.SNSNotification', on_delete=models.SET_NULL, null=True)


class SentEmailsInteractions(models.Model):
    TWITTER = 'TW'
    FACEBOOK = 'FB'
    WHATSAPP = 'WP'
    WEB_PAGE = 'WBP'
    OTHER = 'OT'
    VAKI = 'VAKI'

    INTERACTION_TYPE = [
        (TWITTER, 'Twitter'),
        (FACEBOOK, 'Facebook'),
        (WHATSAPP, 'Whatsapp'),
        (WEB_PAGE, 'Web page'),
        (OTHER, 'Other'),
        (VAKI, 'Vaki')
    ]

    class Meta:
        db_table = 'clicks_tracking'

    mail = models.ForeignKey('mails.Mail', on_delete=models.CASCADE, related_name='interactions')
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='interactions')
    type = models.CharField(max_length=4, choices=INTERACTION_TYPE, default='')
    tinto_block_entry = models.ForeignKey(
        'tintos.TintoBlocksEntries',
        on_delete=models.CASCADE,
        default=None,
        null=True,
        blank=True,
        related_name='interactions'
    )
    link = models.TextField()
    click_date = models.DateTimeField(auto_now_add=True)


class Templates(models.Model):
    """Mail templates model."""
    name = models.CharField(max_length=128, unique=True)
    label = models.CharField(max_length=120, unique=True)
    file_name = models.CharField(max_length=120, unique=True)

    @property
    def html(self):
        """
        Html representation of template. If file does not exist return null
        """
        try:
            display_dict = {
                'html': '{{html}}',
                'email_type': 'Diario',
                'date': get_string_date(datetime.datetime.today())
            }
            template = loader.render_to_string(f'../templates/mailings/{self.file_name}', display_dict)
            return template
        except TemplateDoesNotExist:
            return None

    def __str__(self):
        return f'{self.name} - {self.label}'

    class Meta:
        verbose_name = "Template"
        verbose_name_plural = "Templates"
        ordering = ['name']


class MailLinks(models.Model):
    final_link = models.TextField()
    code = models.TextField(blank=True, default='')

    def mail_link(self):
        """
        Return link to use on email.
        """
        return f"{settings.SERVER_URL}/mails/redirect/{self.code}" + "?user={uuid}"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = generate_random_alphanumeric_code()

        super(MailLinks, self).save(*args, **kwargs)

    def __str__(self):
        return self.final_link

    class Meta:
        verbose_name = "Links de correos"
        verbose_name_plural = "Links de correos"
