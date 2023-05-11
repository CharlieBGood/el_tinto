from rest_framework import viewsets, mixins, status
from rest_framework.response import Response

from el_tinto.mails.models import Mail
from el_tinto.users.models import User
from el_tinto.users.serializers import CreateRegisterSerializer
from el_tinto.utils.send_mail import send_mail
from el_tinto.utils.utils import UTILITY_MAILS, ONBOARDING_EMAIL_NAME, get_email_provider, get_email_provider_link
from el_tinto.utils.views_mixins import SerializerByActionMixin


class RegisterViewset(SerializerByActionMixin, viewsets.GenericViewSet, mixins.CreateModelMixin):
    """Register viewset."""
    queryset = User.objects.all()
    permission_classes = []
    serializer_class_create = CreateRegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)

        validated_data = serializer.validated_data

        response_data = {
            'name': validated_data['first_name'],
            'email_provider': get_email_provider(validated_data['email']),
            'email_provider_link': get_email_provider_link(
                validated_data['email'],
                request.user_agent.is_mobile,
                request.user_agent.device.family
            ),
        }

        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer):
        """
        If user already exists on the system but is inactive, then activate it.
        Else, create the user.
        Send subscription email.
        """
        user = User.objects.filter(email=serializer.validated_data['email'], is_active=False).first()

        if user:
            user.is_active = True
            user.first_name = serializer.validated_data['first_name']
            user.last_name = serializer.validated_data['last_name']
            user.save()

        else:
            user = serializer.save()

        onboarding_mail = Mail.objects.get(id=UTILITY_MAILS.get(ONBOARDING_EMAIL_NAME))

        onboarding_mail.recipients.add(user)

        send_mail(onboarding_mail, [user.email], user)
