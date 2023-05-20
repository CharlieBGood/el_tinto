import json
import os

from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect
from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.views import APIView

from el_tinto.mails.models import Mail
from el_tinto.users.models import User, Unsuscribe
from el_tinto.users.serializers import CreateRegisterSerializer, UpdatePreferredDaysSerializer, \
    ConfirmUpdatePreferredDaysSerializer, DestroyRegisterSerializer, GetReferralHubInfoParams
from el_tinto.utils.html_constants import INVITE_USERS_MESSAGE
from el_tinto.utils.send_mail import send_mail
from el_tinto.utils.users import calculate_referral_race_parameters, get_next_price_info
from el_tinto.utils.utils import UTILITY_MAILS, ONBOARDING_EMAIL_NAME, get_email_provider, get_email_provider_link, \
    CHANGE_PREFERRED_DAYS, get_string_days, MILESTONES


class RegisterView(APIView):
    """Register view."""
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = CreateRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)

        response_data = {
            'user_name': user.user_name,
            'email_provider': get_email_provider(user.email),
            'email_provider_link': get_email_provider_link(
                user.email,
                request.user_agent.is_mobile,
                request.user_agent.device.family
            ),
        }

        return Response(data=response_data, status=status.HTTP_201_CREATED)

    def perform_create(self, serializer):
        """
        If user already exists on the system but is inactive, then activate it.
        Else, create the user.
        Send subscription email.

        "params"
        :serializer: Serializer obj

        :return:
        :user: User obj

        """
        user = User.objects.filter(email=serializer.validated_data['email'], is_active=False).first()

        if user:
            user.is_active = True
            user.first_name = (serializer.validated_data.get('first_name') or user.first_name)
            user.last_name = (serializer.validated_data.get('last_name') or user.last_name)
            user.save()

        else:
            user = serializer.save()

        onboarding_mail = Mail.objects.get(id=UTILITY_MAILS.get(ONBOARDING_EMAIL_NAME))

        send_mail(onboarding_mail, [user.email], user=user)

        onboarding_mail.recipients.add(user)

        return user


class UnsuscribeView(APIView):
    """Unsuscribe view."""
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = DestroyRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.pop('email')

        self.perform_destroy(user, serializer.validated_data)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance, data):
        if Unsuscribe.objects.filter(user=instance).exists():
            Unsuscribe.objects.filter(user=instance).update(**data)
        else:
            Unsuscribe.objects.create(user=instance, **data)

        instance.is_active = False

        instance.save()


class UpdatePreferredDaysView(APIView):
    """Update preferred days view."""
    permission_classes = []

    def patch(self, request, *args, **kwargs):
        serializer = UpdatePreferredDaysSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.pop('email')

        # This works because validated_data is an ordered dict
        days_values = serializer.validated_data.values()

        # Starts on Monday
        day_of_the_week_number = 0

        preferred_email_days = []

        for day in days_values:
            if day:
                preferred_email_days.append(day_of_the_week_number)

            day_of_the_week_number += 1

        data = {
            'email': user.email,
            'preferred_email_days': preferred_email_days
        }

        key = f'{user.email}_change_preferred_days'

        # Add days to cache for 24 hours (60 s * 60 m * 24 h)
        cache.set(key, json.dumps(data), timeout=60*60*24)

        new_preferred_days_numbers = [str(day) for day in preferred_email_days]

        string_days, display_type = get_string_days(new_preferred_days_numbers)

        extra_mail_data = {
            'days': string_days,
            'display_type': display_type,
            'key': f'{user.email}_change_preferred_days'
        }

        change_preferred_email_days_mail = Mail.objects.get(id=UTILITY_MAILS.get(CHANGE_PREFERRED_DAYS))

        send_mail(change_preferred_email_days_mail, [user.email], user=user, extra_mail_data=extra_mail_data)

        change_preferred_email_days_mail.recipients.add(user)

        return redirect(settings.WEB_APP_URL + f'/desuscribirse/personalizar/confirmacion?user_name={user.user_name}')


class ConfirmUpdatePreferredDaysView(APIView):
    """Confirm update preferred days view."""
    permission_classes = []

    def get(self, request, *args, **kwargs):
        serializer = ConfirmUpdatePreferredDaysSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        json_data = cache.get(serializer.validated_data['key'])

        if not json_data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'key': 'Llave inválida.'})

        data = json.loads(json_data)

        try:
            user = User.objects.get(email=data.get('email'))

        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'email': 'El usuario no existe en nuestro sistema'})

        preferred_email_days = data.get('preferred_email_days', [])

        user.preferred_email_days = preferred_email_days

        user.save()

        return redirect(settings.WEB_APP_URL + f'/desuscribirse/personalizar/confirmacion/?user_name={user.user_name}')


class ReferralHubView(APIView):
    """Referral hub view."""
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """Get referral hub info"""
        serializer = GetReferralHubInfoParams(data=self.request.GET)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['email']

        referral_percentage, referral_race_position = calculate_referral_race_parameters(user)

        price_description, pre_price_string, missing_referred_users_for_next_price = get_next_price_info(user)

        referral_hub_data = {
            'referral_code': user.referral_code,
            'referral_count': user.referred_users_count,
            'referral_percentage': referral_percentage,
            'referral_race_position': referral_race_position,
            'env': 'dev.' if os.getenv('DJANGO_CONFIGURATION') == 'Development' else '',
            'invite_users_message': INVITE_USERS_MESSAGE,
            'user_name': user.user_name,
            'price_description': price_description,
            'pre_price_string': pre_price_string,
            'missing_referred_users_for_next_price': missing_referred_users_for_next_price,
            'milestones': MILESTONES
        }

        return Response(status=status.HTTP_200_OK, data=referral_hub_data)
