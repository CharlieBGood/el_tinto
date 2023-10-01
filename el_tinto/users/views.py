import json
import os
from datetime import date, timedelta

from django.conf import settings
from django.core import exceptions
from django.core.cache import cache
from django.shortcuts import redirect
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from el_tinto.mails.models import Mail
from el_tinto.users.models import User, Unsuscribe, UserVisits, UserTier
from el_tinto.users.serializers import CreateRegisterSerializer, UpdatePreferredDaysSerializer, \
    ConfirmUpdatePreferredDaysSerializer, DestroyRegisterSerializer, GetReferralHubInfoParams, \
    SendMilestoneMailSerializer, UserVisitsQueryParamsSerializer, UserVisitsSerializer, \
    UserButtonsInteractionsSerializer, MyTasteClubActionSerializer
from el_tinto.utils.date_time import get_string_date
from el_tinto.utils.html_constants import INVITE_USERS_MESSAGE
from el_tinto.utils.stripe import handle_unsuscribe
from el_tinto.utils.users import calculate_referral_race_parameters, get_next_prize_info, get_milestones_status, \
    create_user_referral_code
from el_tinto.utils.utils import UTILITY_MAILS, ONBOARDING_EMAIL_NAME, get_email_provider, get_email_provider_link, \
    CHANGE_PREFERRED_DAYS, get_string_days, MILESTONES, get_env_value, TASTE_CLUB_TIER_UTILS, \
    TASTE_CLUB_BENEFICIARY_CANCELATION_MAIL


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

        if not user.referral_code:
            user.referral_code = create_user_referral_code(user)
            user.save()

        # send onboarding email
        onboarding_mail_instance = Mail.objects.get(id=UTILITY_MAILS.get(ONBOARDING_EMAIL_NAME))
        mail = onboarding_mail_instance.get_mail_class()
        mail.send_mail(user)

        return user


class UnsuscribeView(APIView):
    """Unsuscribe view."""
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = DestroyRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data.pop('uuid')

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

        user = serializer.validated_data.pop('uuid')

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

        change_preferred_email_days_instance = Mail.objects.get(id=UTILITY_MAILS.get(CHANGE_PREFERRED_DAYS))

        mail = change_preferred_email_days_instance.get_mail_class()

        mail.send_mail(user=user, extra_data=extra_mail_data)

        return Response(status=status.HTTP_200_OK, data={})


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

        user = serializer.validated_data['uuid']

        referral_percentage, referral_race_position = calculate_referral_race_parameters(user)

        prize_description, pre_prize_string, missing_referred_users_for_next_prize = get_next_prize_info(user)

        referral_hub_data = {
            'referral_code': user.referral_code,
            'referral_count': user.referred_users_count,
            'referral_percentage': referral_percentage,
            'referral_race_position': referral_race_position,
            'env': 'dev.' if os.getenv('DJANGO_CONFIGURATION') == 'Development' else '',
            'invite_users_message': INVITE_USERS_MESSAGE,
            'user_name': user.user_name,
            'prize_description': prize_description,
            'pre_prize_string': pre_prize_string,
            'missing_referred_users_for_next_prize': missing_referred_users_for_next_prize,
            'milestones': MILESTONES,
            'milestone_status': get_milestones_status(user)
        }

        return Response(status=status.HTTP_200_OK, data=referral_hub_data)


class SendMilestoneMailView(APIView):
    """Send milestone email view."""
    permission_classes = []

    def post(self, request, *args, **kwargs):
        """Send milestone email"""
        serializer = SendMilestoneMailSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['uuid']

        milestone_mail_instance = serializer.validated_data['milestone']

        mail = milestone_mail_instance.get_mail_class()

        mail.send_mail(user)

        referral_percentage, referral_race_position = calculate_referral_race_parameters(user)

        prize_description, pre_prize_string, missing_referred_users_for_next_prize = get_next_prize_info(user)

        referral_hub_data = {
            'referral_code': user.referral_code,
            'referral_count': user.referred_users_count,
            'referral_percentage': referral_percentage,
            'referral_race_position': referral_race_position,
            'env': 'dev.' if os.getenv('DJANGO_CONFIGURATION') == 'Development' else '',
            'invite_users_message': INVITE_USERS_MESSAGE,
            'user_name': user.user_name,
            'prize_description': prize_description,
            'pre_prize_string': pre_prize_string,
            'missing_referred_users_for_next_prize': missing_referred_users_for_next_prize,
            'milestones': MILESTONES,
            'milestone_status': get_milestones_status(user)
        }

        return Response(status=status.HTTP_200_OK, data=referral_hub_data)


class UserVisitsView(APIView):
    """User visits view."""
    permission_classes = []

    def get(self, request, *args, **kwargs):
        """Count user visits for referral hub."""

        uuid = request.GET.get('user')

        serializer = UserVisitsQueryParamsSerializer(data=request.GET)
        serializer.is_valid(raise_exception=True)

        user_visit = UserVisits.objects.create(**serializer.validated_data)

        env = get_env_value()
        return redirect(f"https://www.{env}eltinto.xyz/referidos/?user={uuid}&user_visit={user_visit.id}")

    def post(self, request, *args, **kwargs):
        """Count user visits."""

        serializer = UserVisitsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        UserVisits.objects.create(**serializer.validated_data)

        return Response(status=status.HTTP_201_CREATED)


class UserButtonsInteractionsView(APIView):
    """User buttons interactions."""
    permission_classes = []

    def post(self, request, *args, **kwargs):
        """Count user buttons interactions."""

        serializer = UserButtonsInteractionsSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        serializer.save()

        return Response(status=status.HTTP_201_CREATED)


class MyTasteClubView(APIView):
    """My taste club view."""
    permission_classes = []

    def get(self, request, uuid, *args, **kwargs):
        """Get user info for taste club"""

        try:
            user = User.objects.get(uuid=uuid)
            user_tier = UserTier.objects.get(user=user, valid_to__gte=date.today())

            available_beneficiaries_places = user_tier.max_beneficiaries - len(user_tier.beneficiaries)

            my_taste_club_data = {
                'id': user_tier.id,
                'user_name': user.user_name,
                'tier': user_tier.tier,
                'tier_name': user_tier.tier_name,
                'valid_to': get_string_date(user_tier.valid_to),
                'is_main_account': True if not user_tier.parent_tier else False,
                'beneficiaries': user_tier.beneficiaries,
                'plan_owner': user_tier.parent_tier.user.email if user_tier.parent_tier else None,
                'will_renew': user_tier.will_renew,
                'available_beneficiaries_places': available_beneficiaries_places,
                'dispatch_time': user.dispatch_time,
                'timezone': user.tzinfo
            }

        except (User.DoesNotExist, exceptions.ValidationError):
            return Response(status=status.HTTP_404_NOT_FOUND, data={'user': "User does not exist."})

        except UserTier.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'user': "User has no active tier."})

        return Response(data=my_taste_club_data)


class MyTasteClubActionsView(APIView):
    """My taste club actions view."""
    permission_classes = []

    def patch(self, request, id, action, *args, **kwargs):
        """
        Execute action over taste club subscription.
        Posible actions:

        - remove_user
        - add_user
        - change_dispatch_time
        """
        try:
            user_tier = UserTier.objects.get(id=id, valid_to__gte=date.today())

            serializer = MyTasteClubActionSerializer(
                context={'action': action, 'user_tier': user_tier}, data=self.request.data
            )

            if serializer.is_valid():
                validated_data = serializer.validated_data

                if action == 'add_user':
                    self._add_user_action(user_tier, validated_data)

                elif action == 'remove_user':
                    self._remove_user_action(user_tier, validated_data)

                elif action == 'change_dispatch_time':
                    self._change_dispatch_time_action(user_tier, validated_data)

                elif action == 'unsuscribe':
                    handle_unsuscribe(user_tier)

                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST, data={'action': 'Invalid action.'})

                available_beneficiaries_places = user_tier.max_beneficiaries - len(user_tier.beneficiaries)

                response_dict = {
                    'id': user_tier.id,
                    'user_name': user_tier.user.user_name,
                    'tier': user_tier.tier,
                    'tier_name': user_tier.tier_name,
                    'valid_to': get_string_date(user_tier.valid_to),
                    'is_main_account': True if not user_tier.parent_tier else False,
                    'beneficiaries': user_tier.beneficiaries,
                    'plan_owner': user_tier.parent_tier.user.email if user_tier.parent_tier else None,
                    'will_renew': user_tier.will_renew,
                    'available_beneficiaries_places': (
                        0 if available_beneficiaries_places < 0 else available_beneficiaries_places
                    ),
                    'dispatch_time': user_tier.user.timezone_aware_dispatch_time,
                    'timezone': user_tier.user.tzinfo
                }

            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data=serializer.errors)

        except UserTier.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'user': "User has no active tier."})

        return Response(data=response_dict)

    def _remove_user_action(self, user_tier, validated_data):
        """
        Remove user action

        :params:
        user_tier: UserTier obj
        validated_data: dict
        """
        remove_user = User.objects.get(email=validated_data['email'])
        remove_tier = user_tier.children_tiers.get(user=remove_user)
        remove_tier.valid_to = date.today() - timedelta(days=1)
        remove_tier.save()

        # send confirmation email
        instance = Mail.objects.get(id=TASTE_CLUB_BENEFICIARY_CANCELATION_MAIL)
        mail = instance.get_mail_class()
        mail.send_mail(user=remove_user)

    def _add_user_action(self, user_tier, validated_data):
        """
        Add user action

        :params:
        user_tier: UserTier obj
        validated_data: dict
        """
        email = validated_data['email']
        user = User.objects.filter(email=email).first()

        # active user if is inactive
        if user and not user.is_active:
            user.is_active = True
            user.save()

        # subscribe user if not already subscribed
        if not user:
            user = User.objects.create(email=email, referred_by=user_tier.user)

            # set user referral code
            user.referral_code = create_user_referral_code(user)
            user.save()

            # send onboarding email
            onboarding_mail_instance = Mail.objects.get(id=UTILITY_MAILS.get(ONBOARDING_EMAIL_NAME))
            mail = onboarding_mail_instance.get_mail_class()
            mail.send_mail(user)

        # Create new tier
        new_user_tier = UserTier.objects.create(
            user=User.objects.get(email=email),
            parent_tier=user_tier,
            tier=user_tier.tier,
            valid_to=user_tier.valid_to,
            missing_sunday_mails=TASTE_CLUB_TIER_UTILS[user_tier.tier]['sunday_mails']
        )

        # send confirmation mail
        tier_mail_id = TASTE_CLUB_TIER_UTILS[user_tier.tier]['invitation_mail']

        if tier_mail_id:
            instance = Mail.objects.get(id=tier_mail_id)
            mail = instance.get_mail_class()

            mail.send_mail(user=new_user_tier.user)

    def _change_dispatch_time_action(self, user_tier, validated_data):
        """
        Add user action

        :params:
        user_tier: UserTier obj
        validated_data: dict
        """
        user_tier.user.dispatch_time = validated_data['dispatch_time']
        user_tier.user.tzinfo = validated_data['tzinfo']
        user_tier.user.save()
