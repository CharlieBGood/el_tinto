from rest_framework.routers import DefaultRouter

from el_tinto.tintos.views import TintoViewSet, TintoBlocksViewSet, TintoBlocksEntriesBlocksViewSet

tintos_router = DefaultRouter()

tintos_router.register(r'tintos', TintoViewSet, basename='tintos')
tintos_router.register(r'tinto-blocks', TintoBlocksViewSet, basename='tintos_blocks')
tintos_router.register('tinto-blocks-entries', TintoBlocksEntriesBlocksViewSet, basename='tintos_blocks_entries')

urlpatterns = tintos_router.urls
