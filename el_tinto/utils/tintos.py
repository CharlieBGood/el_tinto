from django.db.models.signals import post_save
from django.dispatch import receiver

from el_tinto.mails.models import Mail
from el_tinto.tintos.models import TintoBlocksEntries
from el_tinto.utils.utils import TINTO_BLOCK_TYPE_INTRO_ID, TINTO_BLOCK_TYPE_COLOMBIANISM_ID, TINTO_BLOCK_TYPE_NEWS_ID


def generate_tinto_html(tinto):
    """
    Generate html based on the TintoBlocks related to the passed Tinto

    :params:
    tinto: Tinto object

    :return:
    html: str
    """
    html = ''

    for tinto_block_entry in tinto.tintoblocksentries_set.all():
        html += tinto_block_entry.display_html

    return html


def generate_tinto_html_sunday_no_prize(tinto):
    """
    Generate html based on the TintoBlocks related to the passed Tinto
    when user doesn't have the sundays mail prize unlocked.

    :params:
    tinto: Tinto object

    :return:
    html: str
    """
    intro_html = tinto.tintoblocksentries_set.filter(tinto_block__type__id=TINTO_BLOCK_TYPE_INTRO_ID).first()
    colombianism = tinto.tintoblocksentries_set.filter(tinto_block__type__id=TINTO_BLOCK_TYPE_COLOMBIANISM_ID).first()
    first_news = tinto.tintoblocksentries_set.filter(tinto_block__type__id=TINTO_BLOCK_TYPE_NEWS_ID).first()

    html = (
        (intro_html.display_html if intro_html else '') +
        (colombianism.display_html if colombianism else '') +
        (first_news.display_html if first_news else '')
    )

    return html


@receiver(post_save, sender=Mail)
def update_tinto_title(sender, instance, *args, **kwargs):
    """
    Update the title of the corresponding Tinto for the given Mail
    """
    if instance.type == Mail.DAILY:
        try:
            instance.tinto.name = instance.subject
            instance.tinto.save()

        except AttributeError:
            raise AttributeError(f"Mail {instance} has no related Tinto")


@receiver(post_save, sender=TintoBlocksEntries)
def update_mail_html(sender, instance, *args, **kwargs):
    """
    Update the html content of the Mail related to the current
    TintoBlockEntry
    """
    try:
        mail = instance.tinto.mail
        mail.html = generate_tinto_html(instance.tinto)
        mail.save()

    except AttributeError:
        pass
