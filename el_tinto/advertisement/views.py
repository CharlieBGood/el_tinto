from django.http import Http404
from django.shortcuts import redirect
from django.views.decorators.http import require_http_methods

from el_tinto.advertisement.models import Leads


@require_http_methods(["GET"])
def suscribe_lead(request, lead_type):

    if lead_type in [lead_type[0] for lead_type in Leads.SITES]:

        Leads.objects.create(site=lead_type, request_info=request.__dict__)
        return redirect('suscribe')

    else:
        raise Http404()
