from rest_framework import serializers

from el_tinto.tintos.models import TintoBlocks, Tinto
from el_tinto.tintos.serializers.tinto_block_entry_types import TintoBlockTypeSerializer


class TintoBlocksSerializer(serializers.ModelSerializer):
    """TintoBlocks serializer."""
    type = TintoBlockTypeSerializer()

    class Meta:
        model = TintoBlocks
        exclude = ['created_at']


class PatchTintoBlockSerializer(serializers.ModelSerializer):
    """Patch TintoBlocks serializer."""

    class Meta:
        model = TintoBlocks
        exclude = ['created_at']


class CreateTintoBlocksSerializer(serializers.ModelSerializer):
    """Create TintoBlocks serializer."""
    tinto = serializers.PrimaryKeyRelatedField(
        queryset=Tinto.objects.all(),
        required=True,
        allow_null=False,
        write_only=True,
        help_text="This is the Tinto to which the Tinto Block would be related",
    )

    class Meta:
        model = TintoBlocks
        fields = [
            'html',
            'title',
            'type',
            'news_type',
            'tinto'
        ]
