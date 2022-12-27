from rest_framework.routers import DefaultRouter

from el_tinto.tintos.views import (
    TintoViewSet,
    TintoBlocksViewSet,
    TintoBlocksEntriesBlocksViewSet,
    TintoBlockTypeViewSet,
    NewsTypeViewSet
)

tintos_router = DefaultRouter()

tintos_router.register(r'tintos', TintoViewSet, basename='tintos')
tintos_router.register(r'tinto-blocks', TintoBlocksViewSet, basename='tintos_blocks')
tintos_router.register('tinto-blocks-entries', TintoBlocksEntriesBlocksViewSet, basename='tintos_blocks_entries')
tintos_router.register('tinto-block-entry-types', TintoBlockTypeViewSet, basename='tinto_block_entry_types')
tintos_router.register('news-types', NewsTypeViewSet, basename='news_types')

urlpatterns = tintos_router.urls
