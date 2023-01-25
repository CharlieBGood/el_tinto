from django.shortcuts import render

from el_tinto.mails.models import Mail
from el_tinto.tintos.models import TintoBlocksEntries, Tinto
from el_tinto.utils.date_time import get_string_date
from django.views.decorators.http import require_http_methods
from django.utils.safestring import mark_safe
from django.http import Http404


@require_http_methods(["GET"])
def news(request, news_id):

    try:
        tinto_block_entry = TintoBlocksEntries.objects.get(id=news_id)

    except TintoBlocksEntries.DoesNotExist:
        raise Http404()

    try:
        tinto_block_entry.tinto.mail

    except Tinto.mail.RelatedObjectDoesNotExist:
        raise Http404()

    #TODO: Add verification that only correct news can be shared
    if tinto_block_entry.tinto.mail.type != Mail.DAILY:
        raise Http404()

    else:
        return render(request, 'news.html', context=get_news_context(tinto_block_entry))


def get_news_context(tinto_block_entry):
    """
    Get news context

    :params:
    tinto_block_entry: TintoBlockEntry object

    :return:
    news_context: dict
    """
    news_context = {
        'html': mark_safe(tinto_block_entry.display_html),
        'date': get_string_date(tinto_block_entry.tinto.mail.dispatch_date.date()),
    }

    return news_context
