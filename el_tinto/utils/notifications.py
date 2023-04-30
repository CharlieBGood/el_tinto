from django.utils import timezone

from el_tinto.mails.models import SentEmails, SentEmailsInteractions, Mail
from el_tinto.tintos.models import TintoBlocksEntries
from el_tinto.users.models import User
from el_tinto.utils.send_mail import send_mail, get_mail_template, get_mail_template_data
from el_tinto.utils.utils import MILESTONES


def update_sent_email_data(user, mail):
    """
    Update the opened date in the SentEmail instance if it exists.

    :params:
    user: User object
    mail: Mail object

    :return: None
    """
    try:
        sent_email = SentEmails.objects.get(
            user=user,
            mail=mail,
        )
        sent_email.opened_date = timezone.now()
        sent_email.save()

    except SentEmails.DoesNotExist:
        pass


def send_milestone_email(user):
    """
    Send the corresponding email to the user who referred the current user (if exists)
    when it hits one of the milestones.

    :params:
    user: User object

    :return: None
    """
    try:
        referral_user = User.objects.get(id=user.referred_by.id)

        milestone = MILESTONES.get(referral_user.referred_users.count())

        if milestone:
            mail = Mail.objects.get(id=milestone.get('mail_id'))

            html_version = get_mail_template(mail, user)

            if not SentEmails.objects.filter(user=referral_user, mail=mail).exists():

                send_mail(
                    mail,
                    html_version,
                    get_mail_template_data(mail, referral_user),
                    [referral_user.email],
                    user=referral_user
                )

    except User.DoesNotExist:
        pass


def get_or_create_email_interaction(user, mail, click_data):
    """
    Create a new email interaction if one does not exist for the given parameters.

    :params:
    user: User object
    mail: Mail object
    click_data: dict

    :return: None
    """
    try:
        SentEmailsInteractions.objects.get(
            user=user,
            mail=mail,
            type=click_data['linkTags']['type'][0],
            tinto_block_entry=TintoBlocksEntries.objects.filter(
                id=int(click_data['linkTags']['tinto_block_entry'][0])
            ).first() if click_data['linkTags'].get('tinto_block_entry') else None
        )

    except SentEmailsInteractions.DoesNotExist:
        SentEmailsInteractions.objects.create(
            user=user,
            mail=mail,
            link=click_data.get('link'),
            type=click_data['linkTags']['type'][0],
            tinto_block_entry=TintoBlocksEntries.objects.filter(
                id=int(click_data['linkTags']['tinto_block_entry'][0])
            ).first() if click_data['linkTags'].get('tinto_block_entry') else None
        )
