from rest_framework import serializers

from el_tinto.mails.models import Mail
from el_tinto.users.models import User
from el_tinto.utils.utils import MILESTONES


class CreateRegisterSerializer(serializers.ModelSerializer):
    """Create register serializer."""
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False, max_length=25)
    last_name = serializers.CharField(required=False, max_length=25)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'referred_by']

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
        referral_code = data.pop('referral_code', None)

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
