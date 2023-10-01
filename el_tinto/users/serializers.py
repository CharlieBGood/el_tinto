from datetime import datetime, time, date

from pytz import timezone
from rest_framework import serializers

from el_tinto.mails.models import Mail
from el_tinto.users.models import User, UserVisits, UserButtonsInteractions, UserTier
from el_tinto.utils.date_time import convert_datetime_to_local_datetime
from el_tinto.utils.utils import MILESTONES


class CreateRegisterSerializer(serializers.ModelSerializer):
    """Create register serializer."""
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False, max_length=25)
    last_name = serializers.CharField(required=False, max_length=25)
    utm_source = serializers.CharField(required=False, max_length=25, allow_blank=True)
    medium = serializers.CharField(required=False, max_length=25, allow_blank=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'referred_by', 'utm_source', 'medium']

    def validate_email(self, obj):
        """
        Validate that emails is not already registered.
        """
        if User.objects.filter(email=obj, is_active=True).exists():
            raise serializers.ValidationError('Este correo ya está registrado en nuestra base de datos.')

        return obj

    def to_internal_value(self, data):
        """
        Get referral user from referral code.
        """
        referral_code = data.get('referral_code', None)

        if referral_code:

            if not (isinstance(referral_code, str) or len(referral_code) > 6):
                raise ValueError('referral_code no es de tipo válido.')

            try:
                referred_by = User.objects.get(referral_code=referral_code).id

            except User.DoesNotExist:
                referred_by = None

            data['referred_by'] = referred_by

        return super().to_internal_value(data)


class DestroyRegisterSerializer(serializers.Serializer):
    """Destroy register serializer."""
    uuid = serializers.UUIDField()
    boring = serializers.BooleanField(required=False)
    invasive = serializers.BooleanField(required=False)
    variety = serializers.BooleanField(required=False)
    not_used = serializers.BooleanField(required=False)
    other_email = serializers.BooleanField(required=False)
    recommendation = serializers.CharField(required=False, allow_blank=True)

    def validate_uuid(self, obj):
        """
        Validate that user with uuid already exists and is active.
        Return the user.

        :return:
        user: User obj
        """
        try:
            user = User.objects.get(uuid=obj, is_active=True)

        except User.DoesNotExist:
            raise serializers.ValidationError('El usuario no existe en nuestro sistema.')

        return user


class UpdatePreferredDaysSerializer(serializers.Serializer):
    """Update preferred days serializer."""
    monday = serializers.BooleanField(required=False)
    tuesday = serializers.BooleanField(required=False)
    wednesday = serializers.BooleanField(required=False)
    thursday = serializers.BooleanField(required=False)
    friday = serializers.BooleanField(required=False)
    saturday = serializers.BooleanField(required=False)
    sunday = serializers.BooleanField(required=False)
    uuid = serializers.UUIDField()

    def validate_uuid(self, obj):
        """
        Validate that user with uuid already exists and is active.
        Return the user.

        :return:
        user: User obj
        """
        try:
            user = User.objects.get(uuid=obj, is_active=True)

        except User.DoesNotExist:
            raise serializers.ValidationError('El usuario no existe en nuestro sistema.')

        return user

    def validate(self, attrs):
        """Validate that at least one value is not false."""
        days_values = attrs.values()

        if not any(days_values):
            raise ValueError('Debes seleccionar al menos un día.')

        return attrs


class ConfirmUpdatePreferredDaysSerializer(serializers.Serializer):
    """Confirm preferred days serializer."""
    key = serializers.CharField(max_length=128)


class GetReferralHubInfoParams(serializers.Serializer):
    """Get referral hub info params serializer."""
    uuid = serializers.UUIDField()

    def validate_uuid(self, obj):
        """
        Validate that user with uuid already exists and is active.
        Return the user.

        :return:
        user: User obj
        """
        try:
            user = User.objects.get(uuid=obj, is_active=True)

        except User.DoesNotExist:
            raise serializers.ValidationError('El usuario no existe en nuestro sistema.')

        return user


class SendMilestoneMailSerializer(serializers.Serializer):
    """Send milestone mail serializer."""
    uuid = serializers.UUIDField()
    milestone = serializers.ChoiceField(choices=list(MILESTONES.keys()))

    def validate_uuid(self, obj):
        """
        Validate that user with uuid already exists and is active.
        Return the user.

        :return:
        user: User obj
        """
        try:
            user = User.objects.get(uuid=obj, is_active=True)

        except User.DoesNotExist:
            raise serializers.ValidationError('El usuario no existe en nuestro sistema.')

        return user

    def validate_milestone(self, obj):
        """
        Validate that the milestone has an existing mail associated

        :return:
        mail: Mail obj
        """
        try:
            return Mail.objects.get(id=MILESTONES[obj]['mail_id'])

        except Mail.DoesNotExist:
            raise serializers.ValidationError('El premio no existe.')


class UserVisitsQueryParamsSerializer(serializers.Serializer):
    """User visits query params serializer."""

    user = serializers.UUIDField()
    mail = serializers.IntegerField(required=False, allow_null=True)
    type = serializers.ChoiceField(choices=UserVisits.VISIT_TYPES)

    def validate_user(self, obj):
        """
        Validate that user with uuid already exists and is active.
        Return the user.

        :return:
        user: User obj
        """
        try:
            user = User.objects.get(uuid=obj, is_active=True)

        except User.DoesNotExist:
            raise serializers.ValidationError('El usuario no existe en nuestro sistema.')

        return user

    def validate_mail(self, obj):
        """
        Validate that the mail exists.
        Return the mail.

        :return:
        mail: Mail obj
        """
        try:
            mail = Mail.objects.get(id=obj)

        except Mail.DoesNotExist:
            raise serializers.ValidationError('El correo no existe en nuestro sistema.')

        return mail


class UserVisitsSerializer(serializers.Serializer):
    """User visits serializer."""

    user = serializers.CharField()
    type = serializers.ChoiceField(choices=UserVisits.VISIT_TYPES)

    def validate_user(self, obj):
        """
        Validate that user with referral_code already exists and is active.
        Return the user.

        :return:
        user: User obj
        """
        try:
            user = User.objects.get(referral_code=obj, is_active=True)

        except User.DoesNotExist:
            raise serializers.ValidationError('El usuario no existe en nuestro sistema.')

        return user


class UserButtonsInteractionsSerializer(serializers.ModelSerializer):
    """User buttons interactions serializer."""

    class Meta:
        model = UserButtonsInteractions
        fields = ('visit', 'medium', 'type')


class MyTasteClubActionSerializer(serializers.Serializer):
    """My taste club actions serializer."""
    email = serializers.EmailField(required=False)
    dispatch_time = serializers.TimeField(required=False)
    tzinfo = serializers.CharField(required=False)


    def _validate_add_user_action(self, email, user_tier):
        """
        Validate fields for add_user action.

        :params:
        email: str
        user_tier: UserTier obj
        """
        # Validate email field exists
        if not email:
            raise serializers.ValidationError('Email field can not be empty.')

        # Validate parent tier user still can invite more beneficiaries
        if len(user_tier.beneficiaries) >= user_tier.max_beneficiaries:
            raise serializers.ValidationError('No more users allowed on this tier.')

        # Validate beneficiary is not already registered in the program
        user_already_in_program = UserTier.objects.filter(user__email=email, valid_to__gte=date.today()).exists()

        if user_already_in_program:
            raise serializers.ValidationError('User is already in our taste club program.')

    def _validate_remove_user_action(self, email, user_tier):
        """
        Validate fields for remove_user action.

        :params:
        email: str
        user_tier: UserTier obj
        """
        # Validate email field exists
        if not email:
            raise serializers.ValidationError('Email field can not be empty.')

        # Validate email corresponds to beneficiary
        try:
            user_tier.children_tiers.get(user__email=email)

        except UserTier.DoesNotExist:
            raise serializers.ValidationError('Email does not correspond to any beneficiary.')

    def _validate_change_dispatch_time_action(self, dispatch_time, tzinfo, attrs):
        """
        Validate fields for change_dispatch_time action.

        :params:
        dispatch_time: time
        tzinfo: str
        attrs: dict
        """

        if not (dispatch_time and tzinfo):
            raise serializers.ValidationError('Dispatch time and Timezone fields can not be empty.')

        datetime_object = datetime.now(timezone(tzinfo)).replace(
            hour=dispatch_time.hour, minute=dispatch_time.minute, second=0, microsecond=0
        )
        local_datatime = convert_datetime_to_local_datetime(datetime_object).time()

        if local_datatime < time(6, 0, 0):
            raise serializers.ValidationError('Hour must be before 6 am colombian time.')

        attrs.update({'dispatch_time': local_datatime})

    def validate(self, attrs):
        """
        Validate that the respective field is present for each action.

        remove_user, add_user = email
        change_dispatch_time = time
        """
        action = self.context['action']
        user_tier = self.context['user_tier']
        dispatch_time = attrs.get('dispatch_time')
        tzinfo = attrs.get('tzinfo')
        email = attrs.get('email')

        if action == 'add_user':
            self._validate_add_user_action(email, user_tier)

        if action == 'remove_user':
            self._validate_remove_user_action(email, user_tier)

        elif action == 'change_dispatch_time':
            self._validate_change_dispatch_time_action(dispatch_time, tzinfo, attrs)

        return attrs
