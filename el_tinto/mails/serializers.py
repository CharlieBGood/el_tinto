from datetime import datetime

from django.utils.dateparse import parse_datetime

from rest_framework import serializers

from el_tinto.mails.models import Templates, Mail
from el_tinto.utils.date_time import convert_utc_to_local_datetime


class TemplatesSerializer(serializers.ModelSerializer):
    """Templates serializer."""
    html = serializers.CharField()

    class Meta:
        model = Templates
        fields = [
            'name',
            'label',
            'html'
        ]


class MailsSerializer(serializers.ModelSerializer):
    """Mails serializer."""
    html = serializers.CharField(required=False)

    class Meta:
        model = Mail
        fields = '__all__'
        extra_kwargs = {"type": {"required": False}}
