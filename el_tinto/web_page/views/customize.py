from django.urls import resolve
from django.shortcuts import render, redirect
from el_tinto.users.models import User
from el_tinto.mails.models import Mail
from el_tinto.utils.send_mail import send_mail
from el_tinto.utils.utils import DAY_OF_THE_WEEK_MAP, get_string_days
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def customize(request):

    email = request.GET.get('email')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return redirect('index')

    if request.method == 'POST':

        mail = Mail(subject='Cambios en días de envío')

        new_preferred_days_numbers = []

        for day in request.POST.keys():
            if DAY_OF_THE_WEEK_MAP.get(day):
                new_preferred_days_numbers.append(day)

        string_days, display_type = get_string_days(new_preferred_days_numbers)

        context = {
            'name': user.first_name,
            'email': user.email,
            'days': string_days,
            'display_type': display_type,
            'numeric_days': ','.join(new_preferred_days_numbers)
        }

        send_mail(
            mail, 'change_preferred_days.html', context, [user.email],
        )

        return render(
            request,
            'customize.html',
            context={'valid': True, 'name': user.first_name}
        )

    else:
        return render(
            request,
            'customize.html',
            context={
                'email': email,
                'name': user.first_name,
                'unsuscribe': True if resolve(request.path_info).url_name == 'unsuscribe_customize' else False
            }
        )