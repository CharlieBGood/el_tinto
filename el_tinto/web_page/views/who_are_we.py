from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from el_tinto.mails.models import Mail
from el_tinto.users.models import User
from el_tinto.utils.send_mail import send_mail
from el_tinto.utils.utils import get_email_provider, get_email_provider_link
from el_tinto.web_page.forms import UserForm


@require_http_methods(["GET", "POST"])
def who_are_we(request):

    if request.method == "GET":
        return render(request, 'who_are_we.html', context={'who_are_we_active': True})

    if request.method == 'POST':
        form = UserForm(request.POST)
        form.is_valid()

        # User exists already in the database
        try:
            user = User.objects.get(email=form.cleaned_data['email'])

            if user.is_active:
                return render(
                    request,
                    'who_are_we.html',
                    context={'error': 'Este correo ya existe en nuestra base de datos', 'who_are_we_active': True}
                )

            else:
                user.is_active = True
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.save()

                return render(
                    request,
                    'who_are_we.html',
                    context={'valid': True, 'name': user.first_name, 'who_are_we_active': True}
                )

        # User does not exist in the database
        except User.DoesNotExist:

            user = User.objects.create(
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                referred_by=None
            )

            mail = Mail.objects.create(subject='Bienvenid@ a El Tinto', type=Mail.WELCOME)

            mail.recipients.add(user)

            send_mail(
                mail, 'onboarding.html', {'name': user.first_name}, [user.email],
            )

            return render(
                request,
                'suscribe.html',
                context={
                    'valid': True,
                    'name': user.first_name,
                    'who_are_we_active': True,
                    'email_provider': get_email_provider(user.email),
                    'email_provider_link': get_email_provider_link(
                        user.email,
                        request.user_agent.is_mobile,
                        request.user_agent.device.family
                    ),
                }
            )
