from django.db.models.signals import post_save
from django.dispatch import receiver

from el_tinto.mails.models import Mail

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
    Update the title of the corresponding Tinto for the given mail
    """
    if instance.type == Mail.DAILY:
        try:
            instance.tinto.name = instance.subject
            instance.tinto.save()

        except AttributeError:
            raise AttributeError(f"Mail {instance} has no related Tinto")
