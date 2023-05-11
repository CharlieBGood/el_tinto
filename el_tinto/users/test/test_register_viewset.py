from django.urls import reverse
from django.contrib.auth.hashers import check_password
from nose.tools import ok_, eq_
from rest_framework.reverse import reverse_lazy
from rest_framework.test import APITestCase
from rest_framework import status
from faker import Faker
import factory
from ..models import User
from .factories import UserFactory

fake = Faker()


class RegisterViewsetTest(APITestCase):
    """
    Tests Register Viewset.
    """

    def setUp(self):
        self.register_url = 'https://google.com'
        self.user_data = factory.build(dict, FACTORY_CLASS=UserFactory)

    def test_create_user(self):
        """
        Create a user.
        """
        data = {
            "email": self.user_data['email']
        }
        response = self.client.post(self.register_url, data)
