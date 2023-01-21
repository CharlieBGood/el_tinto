from django.db import transaction
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from el_tinto.tintos.models import TintoBlocks, Tinto, TintoBlocksEntries, NewsType, TintoBlockType
from el_tinto.tintos.serializers.tintos import TintoSerializer
from el_tinto.tintos.serializers.tinto_blocks import (
    TintoBlocksSerializer,
    CreateTintoBlocksSerializer,
    PatchTintoBlockSerializer
)
from el_tinto.tintos.serializers.tinto_blocks_entries import (
    TintoBlocksEntriesSerializer,
    RetrieveTintoBlockEntry,
    SwitchPositionsTintoBlocksEntries
)
from el_tinto.tintos.serializers.tinto_block_entry_types import TintoBlockTypeSerializer
from el_tinto.tintos.serializers.news_types import NewsTypeSerializer


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

    @action(detail=True, methods=['GET'], url_path='blocks-entries')
    def get_tinto_blocks_entries(self, request, pk=None):
        tinto = self.get_object()
        tinto_blocks_entries = tinto.tintoblocksentries_set.all()

        serializer = RetrieveTintoBlockEntry(tinto_blocks_entries, many=True)
        return Response(serializer.data)


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

    def get_serializer_class(self):
        """Return specific serializer class depending on the performed action."""
        if self.action == 'create':
            return CreateTintoBlocksSerializer
        elif self.action == 'partial_update':
            return PatchTintoBlockSerializer
        else:
            return TintoBlocksSerializer

    def perform_create(self, serializer):
        tinto = serializer.validated_data.pop('tinto')
        new_tinto_block = serializer.save()

        tinto_blocks_entries_count = tinto.tintoblocksentries_set.count()
        TintoBlocksEntries.objects.create(
            tinto=tinto,
            tinto_block=new_tinto_block,
            position=tinto_blocks_entries_count,
        )


class TintoBlocksEntriesBlocksViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """TintoBlocksEntries viewset."""
    queryset = TintoBlocksEntries.objects.all()
    permission_classes = []
    serializer_class = TintoBlocksEntriesSerializer

    def perform_destroy(self, instance):
        deleted_position = instance.position
        instance.tinto_block.delete()
        instance.delete()

        for tinto_block_entry in TintoBlocksEntries.objects.filter(position__gt=deleted_position):
            tinto_block_entry.position -= 1
            tinto_block_entry.save()

    @action(detail=False, methods=['POST'], url_path='switch-positions')
    def switch_positions(self, request):
        serializer = SwitchPositionsTintoBlocksEntries(data=request.data)
        if serializer.is_valid():
            tinto = serializer.validated_data['tinto']
            old_position = serializer.validated_data['old_position']
            new_position = serializer.validated_data['new_position']

            tinto_block_entry_one = tinto.tintoblocksentries_set.get(position=old_position)
            tinto_block_entry_two = tinto.tintoblocksentries_set.get(position=new_position)

            with transaction.atomic():
                tinto_block_entry_one.position, tinto_block_entry_two.position = \
                    tinto_block_entry_two.position, tinto_block_entry_one.position

                tinto_block_entry_one.save()
                tinto_block_entry_two.save()
        else:
            print(serializer.errors)

        # TODO: Improve response
        return Response()


class TintoBlockTypeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """TintoBlockEntryType viewset."""
    queryset = TintoBlockType.objects.all()
    permission_classes = []
    serializer_class = TintoBlockTypeSerializer


class NewsTypeViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """NewsType viewset."""
    queryset = NewsType.objects.all()
    permission_classes = []
    serializer_class = NewsTypeSerializer

