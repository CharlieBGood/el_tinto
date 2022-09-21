from django.shortcuts import render
from django.views.decorators.http import require_http_methods


@require_http_methods(["GET"])
def faqs(request):
    return render(
        request,
        'faqs.html',
        context={"faqs_active": True}
    )