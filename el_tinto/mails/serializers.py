from rest_framework import serializers

from el_tinto.mails.models import Templates, Mail


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
    """Models serializer."""
    html = serializers.CharField(required=False)

    class Meta:
        model = Mail
        fields = '__all__'
