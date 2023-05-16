from datetime import datetime

from django.shortcuts import redirect
from rest_framework import mixins, viewsets
from rest_framework.exceptions import ValidationError, NotFound

from el_tinto.mails.models import Templates, Mail
from el_tinto.mails.serializers import TemplatesSerializer, MailsSerializer
from el_tinto.utils.tintos import generate_tinto_html
from el_tinto.utils.utils import get_env_value


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
                last_mail = Mail.objects.filter(type=Mail.DAILY).order_by('-dispatch_date').first()
                date = last_mail.dispatch_date.strftime("%d-%m-%Y")

                env = get_env_value()

                return redirect(f"www.{env}eltinto.xyz?date={date}")

        else:
            mails = Mail.objects.filter(type=Mail.DAILY).order_by('-dispatch_date').first()

        return mails

    def perform_create(self, serializer):
        serializer.validated_data['html'] = generate_tinto_html(serializer.validated_data['tinto'])
        serializer.save()
