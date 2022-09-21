import datetime
from django.shortcuts import render
from el_tinto.mails.models import Mail
from el_tinto.utils.date_time import get_string_date
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

            return render(request, 'home.html', context=get_index_context(mail))

        else:
            raise Http404()

    else:
        mails = Mail.objects.filter(type=Mail.DAILY)
        mail = mails.order_by('-created_at')[0]

        return render(request, 'home.html', context=get_index_context(mail))


def get_index_context(mail):
    """
    Get index context

    params:
    :mail: [Mail object]

    return: index_context [dict]
    """
    index_context = {
        'html': mark_safe(mail.html),
        'date': get_string_date(mail.dispatch_date.date()),
        'social_media_date': mail.dispatch_date.date().strftime("%d-%m-%Y"),
        'tweet': mail.tweet,
        'el_tinto': True,
        'email_type': 'Dominguero' if mail.dispatch_date.date().weekday() == 6 else 'Diario'
    }

    return index_context
