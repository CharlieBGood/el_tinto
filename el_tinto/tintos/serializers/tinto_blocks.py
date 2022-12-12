from rest_framework import serializers

from el_tinto.tintos.models import TintoBlocks


class TintoBlocksSerializer(serializers.ModelSerializer):
    """TintoBlocks serializer."""
    class Meta:
        model = TintoBlocks
        fields = '__all__'
