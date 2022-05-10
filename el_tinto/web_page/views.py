from distutils.log import error
from django.shortcuts import render
from el_tinto.users.models import User
from el_tinto.web_page.forms import UserForm
from django.views.decorators.http import require_http_methods

@require_http_methods(["GET", "POST"])
def index(request):
    if request.method == 'POST':
        form=UserForm(request.POST)
        if form.is_valid():
            form.save()
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
