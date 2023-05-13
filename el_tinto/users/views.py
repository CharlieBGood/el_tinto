from rest_framework import viewsets, mixins

from el_tinto.users.models import User
from el_tinto.users.serializers import CreateRegisterSerializer
from el_tinto.utils.views_mixins import SerializerByActionMixin


class Register(viewsets.GenericViewSet, mixins.CreateModelMixin, SerializerByActionMixin):
    """Register viewset."""
    queryset = User.objects.all()
    serializer_class_create = CreateRegisterSerializer

    def perform_create(self, serializer):
        """
        If user already exists on the system but is inactive, then activate it.
        Else, create the user.
        """
        inactive_user = User.objects.filter(email=serializer.validated_data['email'], is_active=False).first()

        if inactive_user:
            inactive_user.is_active = True
            inactive_user.first_name = serializer.validated_data['first_name']
            inactive_user.last_name = serializer.validated_data['last_name']
            inactive_user.save()

        else:
            serializer.save()
