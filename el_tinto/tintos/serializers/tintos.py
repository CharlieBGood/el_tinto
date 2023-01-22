from rest_framework import serializers

from el_tinto.tintos.models import Tinto


class TintoSerializer(serializers.ModelSerializer):
    """Tinto serializer."""
    class Meta:
        model = Tinto
        fields = '__all__'
