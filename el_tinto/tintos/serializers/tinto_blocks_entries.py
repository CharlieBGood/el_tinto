from rest_framework import serializers

from el_tinto.tintos.models import TintoBlocksEntries, Tinto
from el_tinto.tintos.serializers.tinto_blocks import TintoBlocksSerializer


class TintoBlocksEntriesSerializer(serializers.ModelSerializer):
    """TintoBlocksEntries serializer."""
    class Meta:
        model = TintoBlocksEntries
        fields = '__all__'


class RetrieveTintoBlockEntry(serializers.ModelSerializer):
    """Retrieve TintoBlocksEntries serializer."""
    tinto_block = TintoBlocksSerializer()

    class Meta:
        model = TintoBlocksEntries
        fields = '__all__'


class SwitchPositionsTintoBlocksEntries(serializers.Serializer):
    """Switch positions in TintoBlockEntries."""
    tinto = serializers.PrimaryKeyRelatedField(queryset=Tinto.objects.all())
    old_position = serializers.IntegerField(min_value=0)
    new_position = serializers.IntegerField(min_value=0)
