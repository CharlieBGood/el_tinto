import datetime
import os

from django.shortcuts import render
from el_tinto.mails.models import Mail
from el_tinto.users.models import User
from el_tinto.utils.date_time import get_string_date
from django.views.decorators.http import require_http_methods
from django.utils.safestring import mark_safe
from django.http import Http404

from el_tinto.utils.html_constants import INVITE_USERS_MESSAGE
from el_tinto.utils.users import calculate_referred_users_percentage


@require_http_methods(["GET"])
def referral_hub(request):

    email = request.GET.get('email')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        raise Http404

    return render(request, 'referral_hub.html', context=get_referral_hub_context(user))


def get_referral_hub_context(user):
    """
    Get news context

    :params:
    user: User object

    :return:
    referral_hub_context: dict
    """
    referral_hub_context = {
        'referral_code': user.referral_code,
        'referral_count': user.referred_users.count(),
        'referral_percentage': calculate_referred_users_percentage(user),
        'referral_race_position': 21,
        'env': 'dev.' if os.getenv('DJANGO_CONFIGURATION') == 'Development' else '',
        'invite_users_message': INVITE_USERS_MESSAGE,
    }

    return referral_hub_context
