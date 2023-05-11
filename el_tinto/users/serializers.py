from rest_framework import serializers

from el_tinto.users.models import User


class CreateRegisterSerializer(serializers.ModelSerializer):
    """Mails serializer."""
    email = serializers.EmailField()
    first_name = serializers.CharField(required=False, max_length=25)
    last_name = serializers.CharField(required=False, max_length=25)
    referred_by = serializers.SerializerMethodField(required=False)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'referred_by']

    def get_referred_by(self, obj):
        """
        Get referred by user based on the referral code.
        """
        referral_code = obj

        print(referral_code)

        try:
            User.objects.filter(referral_code__iexact=referral_code).first().id

        except User.DoesNotExist:
            return None

    def validate_email(self, obj):
        """
        Validate that emails is not already registered.
        """
        if User.objects.filter(email=obj).exists():
            raise serializers.ValidationError('Este correo ya está registrado en nuestra base de datos.')

        return obj
