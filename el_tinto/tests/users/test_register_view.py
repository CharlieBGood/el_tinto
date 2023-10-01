from django.core import mail
from django.urls import reverse
from rest_framework.status import HTTP_201_CREATED, HTTP_400_BAD_REQUEST
from rest_framework.test import APITestCase

from el_tinto.mails.models import Mail
from el_tinto.tests.users.factories import UserFactory
from el_tinto.users.models import User
from el_tinto.utils.utils import UTILITY_MAILS, ONBOARDING_EMAIL_NAME


class TestRegisterView(APITestCase):
    fixtures = ['mails']

    def setUp(self):
        self.url = reverse('register')
        self.user = UserFactory(referral_code='AKIL89')
        self.welcome_mail = Mail.objects.get(id=UTILITY_MAILS.get(ONBOARDING_EMAIL_NAME))

        self.payload = {
            "email": "testemail@testing.com",
            "first_name": "John",
            "last_name": "Doe",
        }

    def test_create_valid_register(self):

        response = self.client.post(self.url, self.payload, format='json')
        data = response.data

        self.assertEqual(response.status_code, HTTP_201_CREATED)

        self.assertEqual(data['user_name'], self.payload['first_name'])
        self.assertEqual(data['email_provider'], 'testing')
        self.assertIsNone(data['email_provider_link'])

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, self.welcome_mail.subject)

        user = User.objects.last()

        self.assertEqual(user.first_name, self.payload['first_name'])
        self.assertEqual(user.last_name, self.payload['last_name'])
        self.assertEqual(user.email, self.payload['email'])
        self.assertIsNone(user.referred_by)
        self.assertEqual(user.preferred_email_days, [])
        self.assertEqual(user.missing_sunday_mails, 4)

    def test_create_user_referred_by_other_user(self):

        self.payload.update({"referral_code": self.user.referral_code})

        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, HTTP_201_CREATED)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, self.welcome_mail.subject)

        user = User.objects.last()

        self.assertEqual(user.first_name, self.payload['first_name'])
        self.assertEqual(user.last_name, self.payload['last_name'])
        self.assertEqual(user.email, self.payload['email'])
        self.assertEqual(user.referred_by, self.user)

    def test_activate_deactivated_account_and_update_info(self):

        self.user.is_active = False
        self.user.save()

        self.payload.update({
            "email": self.user.email
        })

        response = self.client.post(self.url, self.payload, format='json')

        self.assertEqual(response.status_code, HTTP_201_CREATED)

        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, self.welcome_mail.subject)

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, self.payload['first_name'])
        self.assertEqual(self.user.last_name, self.payload['last_name'])
        self.assertEqual(self.user.email, self.payload["email"])

    def test_create_user_with_already_registered_email(self):

        self.payload.update({"email": self.user.email})

        response = self.client.post(self.url, self.payload, format='json')
        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['email'][0], "This email already exists on our database.")
