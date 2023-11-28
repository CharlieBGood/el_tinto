from datetime import datetime

from django.shortcuts import redirect
from rest_framework import mixins, viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from el_tinto.mails.models import Templates, Mail, MailLinks
from el_tinto.mails.serializers import TemplatesSerializer, MailsSerializer
from el_tinto.users.models import User, UserLinkInteractions
from el_tinto.utils.tintos import generate_tinto_html, generate_tinto_html_sunday_no_prize
from el_tinto.utils.utils import replace_words_in_sentence


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
        validated_data = serializer.validated_data
        validated_data['html'] = generate_tinto_html(validated_data['tinto'])

        # Define mail type based on dispatch date if no value is provided
        validated_data.setdefault(
            'type', Mail.SUNDAY if validated_data['dispatch_date'].date().weekday() == 6 else Mail.DAILY
        )

        instance = serializer.save()

        if instance.type == Mail.SUNDAY:

            html = generate_tinto_html_sunday_no_prize(instance.tinto)

            Mail.objects.create(
                html=html,
                subject=instance.subject,
                type=instance.type,
                version=Mail.SUNDAY_NO_REFERRALS_PRIZE_VERSION,
                tweet=instance.tweet,
                subject_message=instance.subject_message,
                dispatch_date=instance.dispatch_date
            )

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

            instance = Mail.objects.filter(type=Mail.DAILY, dispatch_date__date=date_obj).first()

        else:
            instance = Mail.objects.filter(type=Mail.DAILY).order_by('-dispatch_date').first()

        if not instance:
            return Response(data={}, status=status.HTTP_404_NOT_FOUND)

        mail = instance.get_mail_class()

        mail_data = mail.get_mail_template_data()

        html = mail.template.render(mail_data)

        return Response(data={"html": html}, status=status.HTTP_200_OK)


class MailLinkView(APIView):
    """MailLinkView view."""
    permission_classes = []

    def get(self, request, code, *args, **kwargs):
        """Get mail link and redirect"""
        try:
            mail_link = MailLinks.objects.get(code=code)
            user = User.objects.get(uuid=request.GET.get('user'))
            UserLinkInteractions.objects.create(user=user, link=mail_link)

            return redirect(replace_words_in_sentence(mail_link.final_link, user))

        except MailLinks.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
