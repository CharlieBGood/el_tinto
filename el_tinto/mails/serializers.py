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


class CreateMailSerializer(serializers.ModelSerializer):
    """Create Mail serializer."""
    html = serializers.CharField(required=False)
    dispatch_date = serializers.SerializerMethodField()

    def get_dispatch_date(self, data):
        """
        Cast string into datetime object using UTC-5
        """
        date_time_dispatch_date = parse_datetime(data)

        if date_time_dispatch_date:
            return convert_utc_to_local_datetime(date_time_dispatch_date)
        else:
            raise serializers.ValidationError("Insert a valid datetime object %Y-%M-%DT%H:%M")

    class Meta:
        model = Mail
        fields = '__all__'
