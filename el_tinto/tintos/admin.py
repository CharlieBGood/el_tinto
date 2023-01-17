from django.contrib import admin

from el_tinto.tintos.admin_actions.edit_tinto_in_cms import edit_tinto_in_cms
from el_tinto.tintos.models import TintoBlocks, Tinto, TintoBlocksEntries, NewsType, TintoBlockType


@admin.register(Tinto)
class TintoAdmin(admin.ModelAdmin):
    """"Tinto Admin."""
    actions = [edit_tinto_in_cms]
    exclude = ('html', 'name')


@admin.register(TintoBlocks)
class TintoBlocksAdmin(admin.ModelAdmin):
    """"TintoBlocks Admin."""


@admin.register(TintoBlocksEntries)
class TintoBlocksEntriesAdmin(admin.ModelAdmin):
    """"TintoBlocksEntries Admin."""


@admin.register(TintoBlockType)
class TintoBlockTypeAdmin(admin.ModelAdmin):
    """"TintoBlockType Admin."""


@admin.register(NewsType)
class NewsTypeAdmin(admin.ModelAdmin):
    """"NewsType Admin."""
