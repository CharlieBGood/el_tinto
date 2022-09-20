from django.shortcuts import render, redirect
from el_tinto.users.models import User
from el_tinto.utils.utils import DAY_OF_THE_WEEK_MAP
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def customize_days(request):
    email = request.GET.get('email')
    days = request.GET.get('days').split(',')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return redirect('index')

    new_preferred_days = []

    for day in days:
        if DAY_OF_THE_WEEK_MAP.get(day):
            new_preferred_days.append(day)

    user.preferred_email_days = new_preferred_days
    user.save()

    return render(
        request,
        'finish_customization.html',
        context={'email': email, 'name': user.first_name}
    )