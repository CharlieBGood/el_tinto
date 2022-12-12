from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAdminUser

from el_tinto.tintos.models import TintoBlocks, Tinto, TintoBlocksEntries
from el_tinto.tintos.serializers.tintos import TintoSerializer
from el_tinto.tintos.serializers.tinto_blocks import TintoBlocksSerializer
from el_tinto.tintos.serializers.tinto_blocks_entries import TintoBlocksEntriesSerializer


class TintoViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """Tinto viewset."""
    queryset = Tinto.objects.all()
    permission_classes = []
    serializer_class = TintoSerializer


class TintoBlocksViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """TintoBlocks viewset."""
    queryset = TintoBlocks.objects.all()
    permission_classes = []
    serializer_class = TintoBlocksSerializer


class TintoBlocksEntriesBlocksViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet,
):
    """TintoBlocksEntries viewset."""
    queryset = TintoBlocksEntries.objects.all()
    permission_classes = []
    serializer_class = TintoBlocksEntriesSerializer
