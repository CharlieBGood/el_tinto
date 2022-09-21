from django.shortcuts import render, redirect
from el_tinto.users.models import User, Unsuscribe
from el_tinto.web_page.forms import UnsuscribeForm
from django.views.decorators.http import require_http_methods


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