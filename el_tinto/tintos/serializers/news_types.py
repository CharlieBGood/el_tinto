from rest_framework import serializers

from el_tinto.tintos.models import NewsType


class NewsTypeSerializer(serializers.ModelSerializer):
    """NewsType serializer."""
    class Meta:
        model = NewsType
        fields = '__all__'
