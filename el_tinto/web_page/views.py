from django.shortcuts import render
from django.utils.safestring import mark_safe
from el_tinto.mails.models import Mail
from el_tinto.utils.send_mail import send_email
from el_tinto.web_page.forms import UserForm
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def index(request):
    if request.method == 'POST':
        form=UserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            mail = Mail(subject='Bienvenido a El Tinto')
            
            send_email(
                mail, 
                'onboarding.html', 
                {
                    'name': user.first_name
                }, 
                [user.email],
            )
            
            user.save()
            
            return render(
                request,
                'home.html',
                context={'valid': True}
            )
        else:
            return render(
                request,
                'home.html',
                context={'error': 'Este correo ya existe en nuestra base de datos'}
            )
    
    elif request.method == 'GET':
        return render(
            request,
            'home.html'
        )
        
@require_http_methods(["GET"])
def faqs(request):
    return render(
        request,
        'faqs.html',
        context={"faqs_active": True}
    )
