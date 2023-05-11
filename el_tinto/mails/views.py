from datetime import datetime

from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError, NotFound

from el_tinto.mails.models import Templates, Mail
from el_tinto.mails.serializers import TemplatesSerializer, MailsSerializer
from el_tinto.utils.tintos import generate_tinto_html


class TemplatesViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Templates viewset."""
    queryset = Templates.objects.all()
    permission_classes = []
    serializer_class = TemplatesSerializer


class MailsViewset(mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Mails viewset."""
    queryset = Mail.objects.all()
    permission_classes = []
    serializer_class = MailsSerializer

    def get_queryset(self):
        """Filter mails by date."""
        date = self.request.GET.get('date')

        if date:
            try:
                date_obj = datetime.strptime(date, '%d-%m-%Y')

            except ValueError:
                raise ValidationError({'date': 'Datetime format is not allowed, use DD-MM-YYYYY'})

            mails = Mail.objects.filter(type=Mail.DAILY, dispatch_date__date=date_obj)

            if not mails:
                raise NotFound(detail="There's no email for the current date")

        else:
            mails = Mail.objects.all()

        return mails

    def perform_create(self, serializer):
        serializer.validated_data['html'] = generate_tinto_html(serializer.validated_data['tinto'])
        serializer.save()
