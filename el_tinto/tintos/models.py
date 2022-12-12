from django.db import models
from django.core.validators import MaxValueValidator

from tinymce.models import HTMLField


class TintoBlocks(models.Model):
    """TintoBlocks class."""

    # Type constants
    NEWS = 'News'
    AD = 'Advertisement'
    RECOMMENDATION = 'Recommendation'
    OTHERS = 'Others'

    TYPE_OPTIONS = [
        (NEWS, 'Noticias'),
        (AD, 'Publicidad'),
        (RECOMMENDATION, 'Recomendación'),
        (OTHERS, 'Otros'),
    ]

    # Subtype constants
    NATIONAL_POLITICS = 'National Politics'
    INTERNATIONAL_POLITICS = 'International Politics'
    ECONOMICS = 'Economics'
    SPORTS = 'Sports'
    CULTURE = 'Culture'

    SUBTYPE_OPTIONS = [
        (NATIONAL_POLITICS, 'Política nacional'),
        (INTERNATIONAL_POLITICS, 'Política internacional'),
        (ECONOMICS, 'Económica'),
        (SPORTS, 'Deportes'),
        (CULTURE, 'Cultural'),
    ]

    html = HTMLField()
    title = models.CharField(max_length=256)
    type = models.CharField(
        max_length=30,
        choices=TYPE_OPTIONS,
        default=NEWS
    )
    subtype = models.CharField(
        max_length=30,
        choices=SUBTYPE_OPTIONS,
        default=NATIONAL_POLITICS
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.created_at} - {self.type} - {self.title}'

    class Meta:
        verbose_name = "Bloque de Tinto"
        verbose_name_plural = "Bloques de Tinto"
        ordering = ('created_at', 'type', 'subtype', 'title')


class Tinto(models.Model):
    """Tinto's class."""
    blocks = models.ManyToManyField(
        'tintos.TintoBlocks',
        related_name='tintos',
        through="tintos.TintoBlocksEntries",
        through_fields=('tinto', 'tinto_block'),
        blank=True
    )
    name = models.CharField(max_length=256, default='')
    html = HTMLField(default='', blank=True)
    email_dispatch_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email_dispatch_date} - {self.name}"

    class Meta:
        verbose_name = "Tinto"
        verbose_name_plural = "Tintos"
        ordering = ('email_dispatch_date', 'created_at')


class TintoBlocksEntries(models.Model):
    tinto = models.ForeignKey('tintos.Tinto', on_delete=models.CASCADE)
    tinto_block = models.ForeignKey('tintos.TintoBlocks', on_delete=models.CASCADE)
    position = models.PositiveSmallIntegerField(validators=[MaxValueValidator(10)])
    show_share_buttons = models.BooleanField(default=False)
    show_rate_buttons = models.BooleanField(default=False)
    show_reading_time = models.BooleanField(default=False)
    like = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return f"{self.tinto} - {self.position} - {self.tinto_block}"

    class Meta:
        verbose_name = "Entrada de bloques"
        verbose_name_plural = "Entradas de bloques"
        unique_together = ['tinto', 'position']
        ordering = ('tinto__created_at', 'position')
