from pyexpat import model
from django.db import models

class Mail(models.Model):
    """Mail class."""
    
    #TODO add SQL field for personalized queries
    
    #TODO add programmed emails 
    #TODO Send email for new user
    
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
    C = 'C'
    
    VERSION_OPTIONS = [
        (A, 'A'),
        (B, 'B'),
        (C, 'C')
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
        related_name='sended_emails',
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    dispatch_date = models.DateTimeField(null=True, blank=False)
    programmed = models.BooleanField(default=False)
    
    '''recipients = models.ManyToManyField(
        'users.User',
        related_name='received_emails',
        through="mails.SendedEmails", 
        blank=True
    )'''
    
    class Meta:
        verbose_name = "Mail"
        verbose_name_plural = "Mails"

    def __str__(self):
        return self.type
