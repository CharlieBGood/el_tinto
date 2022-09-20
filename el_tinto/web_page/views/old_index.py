from django.urls import reverse
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def old_index(request):
    date = request.GET.get('date', None)

    if date:
        return redirect(f"{reverse('el_tinto')}?date={date}")

    else:
        return redirect('el_tinto')