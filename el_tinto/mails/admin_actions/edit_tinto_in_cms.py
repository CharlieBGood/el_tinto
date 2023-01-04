from django.conf import settings
from django.contrib import admin, messages
from django.shortcuts import redirect

from el_tinto.utils.decorators import only_one_instance


@admin.action(description='Editar Tinto en CMS')
@only_one_instance
def edit_tinto_in_cms(_, request, queryset):
    """
    Edit the Tinto related to the current Mail using the CMS tool.

    :params:
    request: Request object
    queryset: Tinto queryset

    :return: None
    """
    tinto = queryset.first().tinto

    if not tinto:
        return messages.error(request, "Mail does not have a related Tinto")

    return redirect(f'{settings.LA_CAFETERA_URL}/editar-tinto/{tinto.id}')
