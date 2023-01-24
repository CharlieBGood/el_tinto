from django.db import models
from django.core.validators import MaxValueValidator
from django.db.models import Deferrable

from tinymce.models import HTMLField

from el_tinto.utils.html_constants import LINE_BREAKER, SHARE_NEWS
from el_tinto.utils.utils import replace_info_in_share_news_buttons


class TintoBlocks(models.Model):
    """TintoBlocks class."""
    html = HTMLField()
    title = models.CharField(max_length=256)
    type = models.ForeignKey('TintoBlockType', on_delete=models.SET_NULL, null=True)
    news_type = models.ForeignKey('NewsType', on_delete=models.SET_NULL, default=None, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.created_at} - {self.type} - {self.title}'

    def save(self, *args, **kwargs):
        super(TintoBlocks, self).save(*args, **kwargs)

        # Update TintoBlockEntries related
        for tinto_block_entry in self.tintoblocksentries_set.all():
            tinto_block_entry.save()

    class Meta:
        verbose_name = "Bloque de Tinto"
        verbose_name_plural = "Bloques de Tinto"
        ordering = ('created_at', 'type', 'news_type', 'title')


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
        ordering = ('-email_dispatch_date', 'created_at')


class TintoBlocksEntries(models.Model):
    tinto = models.ForeignKey('tintos.Tinto', on_delete=models.CASCADE)
    tinto_block = models.ForeignKey('tintos.TintoBlocks', on_delete=models.CASCADE)
    display_html = HTMLField(default='', blank=True, null=True)
    position = models.PositiveSmallIntegerField(validators=[MaxValueValidator(10)])
    show_share_buttons = models.BooleanField(default=False)
    show_rate_buttons = models.BooleanField(default=False)
    show_reading_time = models.BooleanField(default=False)
    like = models.BooleanField(null=True, blank=True)
    break_line = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.tinto} - {self.position} - {self.tinto_block}"

    def create_tinto_block_entry_html_extra_features(self):
        """
        Create TintoBlockEntry html based on the configuration
        defined in its parameters
        """
        tinto_block_html = self.tinto_block.html

        if self.show_share_buttons:
            tinto_block_html += replace_info_in_share_news_buttons(SHARE_NEWS, self)

        if self.break_line:
            tinto_block_html += LINE_BREAKER

        self.display_html = tinto_block_html

    def save(self, *args, **kwargs):
        # Add extra features to display html
        self.create_tinto_block_entry_html_extra_features()
        super(TintoBlocksEntries, self).save(*args, **kwargs)

    class Meta:
        verbose_name = "Entrada de bloques"
        verbose_name_plural = "Entradas de bloques"
        constraints = (
            models.UniqueConstraint(
                fields=['tinto', 'position'],
                name='unique_position_in_tinto',
                deferrable=Deferrable.DEFERRED
            ),
        )
        ordering = ('tinto__created_at', 'position')


class TintoBlockType(models.Model):
    """
    Type of entry regarding a TintoBlock
    """
    name = models.CharField(max_length=128, unique=True)
    label = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return f"{self.name} - {self.label}"

    class Meta:
        verbose_name = "Tipo de Bloque"
        verbose_name_plural = "Tipos de Bloque"
        ordering = ('name',)


class NewsType(models.Model):
    """
    Type of news.
    """
    name = models.CharField(max_length=128, unique=True)
    label = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return f"{self.name} - {self.label}"

    class Meta:
        verbose_name = "Tipo de historia"
        verbose_name_plural = "Tipos de historias"
        ordering = ('name',)
