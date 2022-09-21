from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def who_are_we(request):
    return render(request, 'who_are_we.html', context={'who_are_we_active': True})
