import os

from django.shortcuts import render, redirect
from el_tinto.users.models import User
from django.views.decorators.http import require_http_methods
from django.http import Http404

from el_tinto.utils.html_constants import INVITE_USERS_MESSAGE
from el_tinto.utils.users import calculate_referral_race_parameters


@require_http_methods(["GET"])
def referral_hub(request):

    email = request.GET.get('email')

    if email == "mateoyepeserna@gmail.com":
        return redirect('index')

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

    referral_percentage, referral_race_position = calculate_referral_race_parameters(user)

    referral_hub_context = {
        'referral_code': user.referral_code,
        'referral_count': user.referred_users_count,
        'referral_percentage': referral_percentage,
        'referral_race_position': referral_race_position,
        'env': 'dev.' if os.getenv('DJANGO_CONFIGURATION') == 'Development' else '',
        'invite_users_message': INVITE_USERS_MESSAGE,
        'username': user.user_name
    }

    return referral_hub_context
