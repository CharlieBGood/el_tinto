from django.contrib import admin

from el_tinto.tintos.admin_actions.edit_tinto_in_cms import edit_tinto_in_cms
from el_tinto.tintos.models import TintoBlocks, Tinto, TintoBlocksEntries, NewsType, TintoBlockType


@admin.register(Tinto)
class TintoAdmin(admin.ModelAdmin):
    """"Tinto Admin."""
    actions = [edit_tinto_in_cms]
    exclude = ('html', 'name')

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        if request.user.groups.filter(name__in=['Editor', 'Founder']):
            return super(TintoAdmin, self).get_model_perms(request)
        else:
            return {}


@admin.register(TintoBlocks)
class TintoBlocksAdmin(admin.ModelAdmin):
    """"TintoBlocks Admin."""

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        if request.user.groups.filter(name__in=['Founder']):
            return super(TintoBlocksAdmin, self).get_model_perms(request)
        else:
            return {}


@admin.register(TintoBlocksEntries)
class TintoBlocksEntriesAdmin(admin.ModelAdmin):
    """"TintoBlocksEntries Admin."""

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        if request.user.groups.filter(name__in=['Founder']):
            return super(TintoBlocksEntriesAdmin, self).get_model_perms(request)
        else:
            return {}


@admin.register(TintoBlockType)
class TintoBlockTypeAdmin(admin.ModelAdmin):
    """"TintoBlockType Admin."""

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        if request.user.groups.filter(name__in=['Founder']):
            return super(TintoBlockTypeAdmin, self).get_model_perms(request)
        else:
            return {}


@admin.register(NewsType)
class NewsTypeAdmin(admin.ModelAdmin):
    """"NewsType Admin."""

    def get_model_perms(self, request):
        """
        Return empty perms dict thus hiding the model from admin index.
        """
        if request.user.groups.filter(name__in=['Founder', 'Editor']):
            return super(NewsTypeAdmin, self).get_model_perms(request)
        else:
            return {}