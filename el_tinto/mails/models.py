from django.db import models

class Mail(models.Model):
    """Mail class."""
    
    html = models.TextField()
    subject = models.CharField(max_length=256, default='')
    type = models.CharField(max_length=50)
    created_by = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Mail"
        verbose_name_plural = "Mails"

    def __str__(self):
        return self.type
