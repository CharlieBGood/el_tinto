import datetime
from django.shortcuts import render, redirect
from el_tinto.users.models import User, Unsuscribe
from el_tinto.mails.models import Mail
from el_tinto.utils.send_mail import send_email
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
                    'date': mail.dispatch_date.date().strftime("%d/%m/%Y"),
                    'tweet': mail.tweet,
                    'el_tinto': True
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
                'date': mail.dispatch_date.date().strftime("%d/%m/%Y"),
                'social_media_date': '?date='+mail.dispatch_date.date().strftime("%d-%m-%Y"),
                'tweet': mail.tweet,
                'el_tinto': True
            }
        ) 
    
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
        form=UserForm(request.POST)
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
                context={'valid': True, 'name': user.first_name, 'suscribe_active': True}
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
        form=UnsuscribeForm(request.POST)
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
                    unsuscribe_instance.recomendation = form.cleaned_data['recomendation']
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

def error_404_view(request, exception):
   
    # we add the path to the the 404.html file
    # here. The name of our HTML file is 404.html
    return render(request, '404.html')

def error_500_view(request):
   
    # we add the path to the the 500.html file
    # here. The name of our HTML file is 404.html
    return render(request, '500.html')