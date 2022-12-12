from rest_framework import serializers

from el_tinto.tintos.models import TintoBlocksEntries


class TintoBlocksEntriesSerializer(serializers.ModelSerializer):
    """TintoBlocksEntries serializer."""
    class Meta:
        model = TintoBlocksEntries
        fields = '__all__'
