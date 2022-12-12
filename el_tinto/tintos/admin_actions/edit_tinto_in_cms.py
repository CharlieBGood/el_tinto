from django.contrib import admin
from django.shortcuts import redirect

from el_tinto.utils.decorators import only_one_instance


@admin.action(description='Editar Tinto en CMS')
@only_one_instance('edit_tinto_in_cms')
def edit_tinto_in_cms(_, request, queryset):
    """
    Edit a Tinto using the CMS tool.

    :params:
    request: Request object
    queryset: Tinto queryset

    :return: None
    """
    tinto = queryset.first()

    return redirect(f'https://google.com/{tinto.id}')
