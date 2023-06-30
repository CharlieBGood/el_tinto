from datetime import datetime

from django.template import loader
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from el_tinto.mails.models import Templates, Mail
from el_tinto.mails.serializers import TemplatesSerializer, MailsSerializer
from el_tinto.utils.send_mail import get_mail_template_data, get_mail_template
from el_tinto.utils.tintos import generate_tinto_html, generate_tinto_html_sunday_no_prize


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
                mails = Mail.objects.none()

        else:
            mails = Mail.objects.filter(type=Mail.DAILY).order_by('-dispatch_date').first()

        return mails

    def perform_create(self, serializer):
        serializer.validated_data['html'] = generate_tinto_html(serializer.validated_data['tinto'])
        instance = serializer.save()

        # if instance.type == Mail.SUNDAY:
        #
        #     html = generate_tinto_html_sunday_no_prize(instance.tinto)
        #
        #     Mail.objects.create(
        #         html=html,
        #         subject=instance.subject,
        #         type=instance.type,
        #         version=Mail.SUNDAY_NO_REFERRALS_PRIZE,
        #         tweet=instance.tweet,
        #         subject_message=instance.subject_message
        #     )

    @action(detail=False, methods=['get'])
    def get_todays_tinto(self, request):
        """
        Get full Tinto html to display in web.
        If no date is provided, get today's Tinto.
        If today's Tinto is not found, get the latest Tinto.
        """
        date = self.request.GET.get('date')

        if date:
            try:
                date_obj = datetime.strptime(date, '%d-%m-%Y')

            except ValueError:
                raise ValidationError({'date': 'Datetime format is not allowed, use DD-MM-YYYYY'})

            mail = Mail.objects.filter(type=Mail.DAILY, dispatch_date__date=date_obj).first()

        else:
            mail = Mail.objects.filter(type=Mail.DAILY).order_by('-dispatch_date').first()

        if not mail:
            return Response(data={}, status=status.HTTP_404_NOT_FOUND)

        if mail.sent_datetime.date().weekday() == 6:
            return Response(data={'mail': 'Sunday mail is not available'}, status=status.HTTP_400_BAD_REQUEST)

        html_file = get_mail_template(mail, None)

        template = loader.get_template(f'../templates/mailings/{html_file}')

        mail_data = get_mail_template_data(mail, None, {"mail_version": False})

        html = template.render(mail_data)

        return Response(data={"html": html}, status=status.HTTP_200_OK)
