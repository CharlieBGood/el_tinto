import datetime
from django.urls import reverse, resolve
from django.shortcuts import render, redirect
from el_tinto.users.models import User, Unsuscribe
from el_tinto.mails.models import Mail
from el_tinto.utils.datetime import get_string_date
from el_tinto.utils.send_mail import send_email
from el_tinto.utils.utils import DAY_OF_THE_WEEK_MAP, get_string_days, get_email_provider, get_email_provider_link
from el_tinto.web_page.forms import UserForm, UnsuscribeForm
from django.views.decorators.http import require_http_methods
from django.utils.safestring import mark_safe
from django.http import Http404


@require_http_methods(["GET"])
def index(request):

    date = request.GET.get('date', None)

    if date:
        date_obj = datetime.datetime.strptime(date, '%d-%m-%Y')
        mails = Mail.objects.filter(type=Mail.DAILY, dispatch_date__date=date_obj)

        if mails:
            mail = mails.order_by('-created_at')[0]

            return render(
                request,
                'home.html',
                context={
                    'html': mark_safe(mail.html),
                    'date': get_string_date(mail.dispatch_date.date()),
                    'social_media_date': mail.dispatch_date.date().strftime("%d-%m-%Y"),
                    'tweet': mail.tweet,
                    'el_tinto': True,
                    'email_type': 'Dominguero' if mail.dispatch_date.date().weekday() == 6 else 'Diario'
                }
            )
        else:
            raise Http404()

    else:
        mails = Mail.objects.filter(type=Mail.DAILY)
        mail = mails.order_by('-created_at')[0]

        return render(
            request,
            'home.html',
            context={
                'html': mark_safe(mail.html),
                'date': get_string_date(mail.dispatch_date.date()),
                'social_media_date': mail.dispatch_date.date().strftime("%d-%m-%Y"),
                'tweet': mail.tweet,
                'el_tinto': True,
                'email_type': 'Dominguero' if mail.dispatch_date.date().weekday() == 6 else 'Diario'
            }
        )


@require_http_methods(["GET"])
def old_index(request):
    date = request.GET.get('date', None)

    if date:
        return redirect(f"{reverse('el_tinto')}?date={date}")

    else:
        return redirect('el_tinto')


@require_http_methods(["GET"])
def who_are_we(request):
    return render(
        request,
        'who_are_we.html',
        context={'who_are_we_active': True}
    )


@require_http_methods(["GET", "POST"])
def suscribe(request):

    if request.method == 'POST':
        form = UserForm(request.POST)
        form.is_valid()
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

        except User.DoesNotExist:
            user = User.objects.create(
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name']
            )
            mail = Mail(subject='Bienvenido a El Tinto')

            send_email(
                mail, 'onboarding.html', {'name': user.first_name}, [user.email],
            )

            user.save()
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
            context={'suscribe_active': True}
        )


@require_http_methods(["GET", "POST"])
def unsuscribe(request):
    if request.method == 'POST':
        form = UnsuscribeForm(request.POST)
        if form.is_valid():
            try:
                user = User.objects.get(email=form.cleaned_data.pop('email'))
                if Unsuscribe.objects.filter(user=user).exists():
                    unsuscribe_instance = Unsuscribe.objects.get(user=user)
                    unsuscribe_instance.boring = form.cleaned_data['boring']
                    unsuscribe_instance.invasive = form.cleaned_data['invasive']
                    unsuscribe_instance.variety = form.cleaned_data['variety']
                    unsuscribe_instance.not_used = form.cleaned_data['not_used']
                    unsuscribe_instance.other_email = form.cleaned_data['other_email']
                    unsuscribe_instance.recommendation = form.cleaned_data['recommendation']
                    unsuscribe_instance.save()
                else:
                    unsuscribe_instance = form.save(commit=False)
                    unsuscribe_instance.user = user
                    unsuscribe_instance.save()

                user.is_active = False
                user.save()
            except User.DoesNotExist:
                pass

        return redirect('index')

    elif request.method == 'GET':
        email = request.GET.get('email', None)
        if email:
            try:
                user = User.objects.get(email=email)
                if user.is_active:
                    return render(
                        request,
                        'unsuscribe.html',
                        context={'user': user}
                    )
            except User.DoesNotExist:
                pass

        return redirect('index')


@require_http_methods(["GET"])
def faqs(request):
    return render(
        request,
        'faqs.html',
        context={"faqs_active": True}
    )


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

        send_email(
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


def error_404_view(request, exception):
    # we add the path to the 404.html file
    # here. The name of our HTML file is 404.html
    return render(request, '404.html')


def error_500_view(request):

    # we add the path to the 500.html file
    # here. The name of our HTML file is 404.html
    return render(request, '500.html')
