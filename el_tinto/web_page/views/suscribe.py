from django.shortcuts import render
from el_tinto.users.models import User
from el_tinto.mails.models import Mail
from el_tinto.utils.send_mail import send_mail
from el_tinto.utils.utils import get_email_provider, get_email_provider_link
from el_tinto.web_page.forms import UserForm
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET", "POST"])
def suscribe(request):

    if request.method == 'POST':
        form = UserForm(request.POST)
        form.is_valid()

        # User exists already in the database
        try:
            user = User.objects.get(email=form.cleaned_data['email'])

            if user.is_active:
                return render(
                    request,
                    'suscribe.html',
                    context={'error': 'Este correo ya existe en nuestra base de datos', 'suscribe_active': True}
                )

            else:
                user.is_active = True
                user.first_name = form.cleaned_data['first_name']
                user.last_name = form.cleaned_data['last_name']
                user.save()

                return render(
                    request,
                    'suscribe.html',
                    context={'valid': True, 'name': user.first_name, 'suscribe_active': True}
                )

        # User does not exist in the database
        except User.DoesNotExist:
            referred_by = None

            if form.cleaned_data.get('referral_code'):
                try:
                    # Find user by referral code without taking into account case-sensitive search
                    referred_by = User.objects.get(referral_code__iexact=form.cleaned_data['referral_code'])

                except User.DoesNotExist:
                    return render(
                        request,
                        'suscribe.html',
                        context={
                            'error': 'El código de referido no corresponde a ningún usuario',
                            'suscribe_active': True
                        }
                    )

            user = User.objects.create(
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                referred_by=referred_by
            )

            mail = Mail.objects.create(subject='Bienvenido a El Tinto', type=Mail.WELCOME)

            send_mail(
                mail, 'onboarding.html', {'name': user.first_name}, [user.email],
            )
            
            return render(
                request,
                'suscribe.html',
                context={
                    'valid': True,
                    'name': user.first_name,
                    'suscribe_active': True,
                    'email_provider': get_email_provider(user.email),
                    'email_provider_link': get_email_provider_link(
                        user.email,
                        request.user_agent.is_mobile,
                        request.user_agent.device.family
                    ),
                }
            )

    elif request.method == 'GET':
        return render(
            request,
            'suscribe.html',
            context={'suscribe_active': True, 'referral_code': request.GET.get('referral_code')}
        )