from rest_framework import serializers

from el_tinto.tintos.models import TintoBlockType


class TintoBlockTypeSerializer(serializers.ModelSerializer):
    """TintoBlockType serializer."""
    class Meta:
        model = TintoBlockType
        fields = '__all__'
