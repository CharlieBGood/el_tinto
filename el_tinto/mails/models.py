from operator import mod
from pyexpat import model
from statistics import mode
from django.db import models

class Mail(models.Model):
    """Mail class."""
    
    #TODO add SQL field for personalized queries
    
    # Type constants
    DAILY = 'Daily'
    TEST = 'Test'
    PROMOTION = 'Promotion'
    
    TYPE_OPTIONS = [
        (DAILY, 'Diario'),
        (TEST, 'Testeo'),
        (PROMOTION, 'Promoción')
    ]
    
    # Version constants
    A = 'A'
    B = 'B'
    DEFUALT_TESTING = 'DEFAULT'
    
    VERSION_OPTIONS = [
        (A, 'A'),
        (B, 'B'),
        (DEFUALT_TESTING, 'Testeo en blanco')
    ]
    
    html = models.TextField()
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
    programmed = models.BooleanField(default=False, editable = False)

    tweet = models.CharField(max_length=255, default='', help_text='255 characters max')
    subject_message = models.CharField(max_length=128, default='', help_text='Texto que acompaña al subject')
    
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
        return f'{self.type} - {self.created_at.strftime("%d-%m/%Y")}'


class SentEmails(models.Model):
    
    mail = models.ForeignKey('mails.Mail', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    opened_date = models.DateTimeField(default=None, null=True)


class SentEmailsInteractions(models.Model):

    TWITTER = 'TW'
    FACEBOOK = 'FB'
    WHATSAPP = 'WP'
    WEB_PAGE = 'WBP'
    OTHER = 'OT'

    INTERACTION_TYPE = [
        (TWITTER, 'Twitter'),
        (FACEBOOK, 'Facebook'),
        (WHATSAPP, 'Whatsapp'),
        (WEB_PAGE, 'Web page'),
        (OTHER, 'Other')
    ]

    class Meta:
        db_table = 'clicks_tracking'

    mail = models.ForeignKey('mails.Mail', on_delete=models.CASCADE)
    user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    type = models.CharField(max_length=3, choices=INTERACTION_TYPE, default='')
    link = models.TextField()
    click_date = models.DateTimeField(auto_now_add=True)