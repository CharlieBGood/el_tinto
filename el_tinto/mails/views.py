from rest_framework import mixins, viewsets

from el_tinto.mails.models import Templates, Mail
from el_tinto.mails.serializers import TemplatesSerializer, MailsSerializer
from el_tinto.utils.tintos import generate_tinto_html


class TemplatesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Templates viewset."""
    queryset = Templates.objects.all()
    permission_classes = []
    serializer_class = TemplatesSerializer


class MailsViewset(mixins.CreateModelMixin, viewsets.GenericViewSet):
    """Mails viewset."""
    queryset = Mail.objects.all()
    permission_classes = []
    serializer_class = MailsSerializer

    def perform_create(self, serializer):
        serializer.validated_data['html'] = generate_tinto_html(serializer.validated_data['tinto'])
        serializer.save()
