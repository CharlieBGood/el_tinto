from django.db.models.signals import post_save
from django.dispatch import receiver

from el_tinto.mails.models import Mail
from el_tinto.tintos.models import TintoBlocksEntries

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
