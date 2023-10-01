from datetime import datetime, timedelta, time

from django.core import mail
from django.template import loader
from django.urls import reverse
from mock.mock import patch
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND
from rest_framework.test import APITestCase

from el_tinto.mails.models import Mail
from el_tinto.tests.stripe.factories import StripePaymentFactory
from el_tinto.tests.users.factories import UserFactory, UserTierFactory
from el_tinto.users.models import UserTier, User
from el_tinto.utils.date_time import get_string_date
from el_tinto.utils.utils import UTILITY_MAILS, ONBOARDING_EMAIL_NAME, TASTE_CLUB_TIER_TINTO_INVITATION_MAIL, \
    TASTE_CLUB_TIER_EXPORTATION_COFFEE_INVITATION_MAIL, replace_words_in_sentence, \
    TASTE_CLUB_BENEFICIARY_CANCELATION_MAIL, TASTE_CLUB_OWNER_CANCELATION_MAIL


def get_template(template_name):
    template_path = f'../../mails/templates/mailings/{template_name}.html'

    return loader.get_template(template_path)


class TestMyTasteClubActionsView(APITestCase):
    fixtures = ['mails']

    def setUp(self):
        self.user = UserFactory(referral_code='AKIL89', tzinfo='America/Lima', dispatch_time=time(6, 0))
        self.user_tier = UserTierFactory(user=self.user, tier=UserTier.TIER_EXPORTATION_COFFEE)
        self.stripe_payment = StripePaymentFactory(user=self.user, user_tier=self.user_tier)

        self.welcome_mail = Mail.objects.get(id=UTILITY_MAILS.get(ONBOARDING_EMAIL_NAME))
        self.tinto_invitation_mail = Mail.objects.get(id=TASTE_CLUB_TIER_TINTO_INVITATION_MAIL)
        self.exportation_coffee_invitation_mail = Mail.objects.get(id=TASTE_CLUB_TIER_EXPORTATION_COFFEE_INVITATION_MAIL)
        self.remove_beneficiary_mail = Mail.objects.get(id=TASTE_CLUB_BENEFICIARY_CANCELATION_MAIL)
        self.unsuscribe_mail = Mail.objects.get(id=TASTE_CLUB_OWNER_CANCELATION_MAIL)

        self.add_user_url = reverse('my_taste_club_actions', args=[self.user_tier.id, 'add_user'])
        self.remove_user_url = reverse('my_taste_club_actions', args=[self.user_tier.id, 'remove_user'])
        self.change_dispatch_time_url = reverse(
            'my_taste_club_actions', args=[self.user_tier.id, 'change_dispatch_time']
        )
        self.unsuscribe_url = reverse('my_taste_club_actions', args=[self.user_tier.id, 'unsuscribe'])

        self.info_email = '☕ El Tinto Pruebas <info@dev.eltinto.xyz>'

    def test_add_user_with_no_more_users_allowed_in_tier(self):
        """
        Add a user to a tier that has already reached the maximum amount of
        beneficiaries allowed
        """
        UserTierFactory(parent_tier=self.user_tier)
        UserTierFactory(parent_tier=self.user_tier)
        UserTierFactory(parent_tier=self.user_tier)

        new_user = UserFactory()

        response = self.client.patch(self.add_user_url, {'email': new_user.email})

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'No more users allowed on this tier.')

    def test_add_user_with_no_more_users_allowed_in_tier_for_tinto_tier(self):
        """
        Add a user to a tier (UserTier.TIER_TINTO) that has already reached the maximum amount of
        beneficiaries allowed.
        """
        self.user_tier.tier = UserTier.TIER_TINTO
        self.user_tier.save()

        UserTierFactory(parent_tier=self.user_tier)

        new_user = UserFactory()

        response = self.client.patch(self.add_user_url, {'email': new_user.email})

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'No more users allowed on this tier.')

    def test_add_user_that_is_already_registered_in_program(self):
        """
        Add a user that already has an active subscription to the program.
        """
        new_user_tier = UserTierFactory()

        response = self.client.patch(self.add_user_url, {'email': new_user_tier.user.email})

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'User is already in our taste club program.')

    def test_add_user_for_inactive_user(self):
        """
        Test add user action for a user that is already subscribed but is inactive.
        """
        new_user = UserFactory(is_active=False)

        response = self.client.patch(self.add_user_url, {'email': new_user.email})

        self.assertEqual(response.status_code, HTTP_200_OK)

        new_user.refresh_from_db()
        self.assertTrue(new_user.is_active)

        new_tier = UserTier.objects.get(user=new_user)
        self.assertEqual(new_tier.tier, self.user_tier.tier)
        self.assertEqual(new_tier.valid_to, self.user_tier.valid_to)
        self.assertEqual(new_tier.parent_tier, self.user_tier)

        data = response.data

        self.assertEqual(data['id'], self.user_tier.id)
        self.assertEqual(data['user_name'], self.user.user_name)
        self.assertEqual(data['tier'], self.user_tier.tier)
        self.assertEqual(data['tier_name'], self.user_tier.tier_name)
        self.assertEqual(data['valid_to'], get_string_date(self.user_tier.valid_to))
        self.assertTrue(data['is_main_account'])
        self.assertEqual(data['beneficiaries'], self.user_tier.beneficiaries)
        self.assertIsNone(data['plan_owner'])
        self.assertEqual(data['will_renew'], self.user_tier.will_renew)
        self.assertEqual(data['available_beneficiaries_places'], self.user_tier.max_beneficiaries - 1)
        self.assertEqual(data['dispatch_time'], self.user.dispatch_time)
        self.assertEqual(data['timezone'], self.user.tzinfo)

        self.assertEqual(len(mail.outbox), 1)
        sent_mail = mail.outbox[0]

        mail_class = self.exportation_coffee_invitation_mail.get_mail_class()
        mail_data = mail_class.get_mail_template_data(new_user)
        html = get_template('survey').render(mail_data)

        exportation_coffee_invitation_mail_subject = replace_words_in_sentence(
            self.exportation_coffee_invitation_mail.subject, user=new_user
        )

        self.assertEqual(sent_mail.subject, exportation_coffee_invitation_mail_subject)
        self.assertEqual(sent_mail.body, html)
        self.assertEqual(sent_mail.from_email, self.info_email)

    def test_add_user_for_new_user(self):
        """
        Test add user action for a user that does not exist on the db.
        """
        response = self.client.patch(self.add_user_url, {'email': 'johndoe@testing.com'})

        self.assertEqual(response.status_code, HTTP_200_OK)

        new_user = User.objects.get(email='johndoe@testing.com')

        new_tier = UserTier.objects.get(user=new_user)
        self.assertEqual(new_tier.tier, self.user_tier.tier)
        self.assertEqual(new_tier.valid_to, self.user_tier.valid_to)
        self.assertEqual(new_tier.parent_tier, self.user_tier)

        data = response.data

        self.assertEqual(data['id'], self.user_tier.id)
        self.assertEqual(data['user_name'], self.user.user_name)
        self.assertEqual(data['tier'], self.user_tier.tier)
        self.assertEqual(data['tier_name'], self.user_tier.tier_name)
        self.assertEqual(data['valid_to'], get_string_date(self.user_tier.valid_to))
        self.assertTrue(data['is_main_account'])
        self.assertEqual(data['beneficiaries'], self.user_tier.beneficiaries)
        self.assertIsNone(data['plan_owner'])
        self.assertEqual(data['will_renew'], self.user_tier.will_renew)
        self.assertEqual(data['available_beneficiaries_places'], self.user_tier.max_beneficiaries - 1)
        self.assertEqual(data['dispatch_time'], self.user.dispatch_time)
        self.assertEqual(data['timezone'], self.user.tzinfo)

        self.assertEqual(len(mail.outbox), 2)
        welcome_mail = mail.outbox[0]
        confirmation_mail = mail.outbox[1]

        # Validate welcome mail
        welcome_mail_class = self.welcome_mail.get_mail_class()
        welcome_mail_data = welcome_mail_class.get_mail_template_data(new_user)
        welcome_mail_html = get_template('onboarding').render(welcome_mail_data)

        welcome_mail_subject = replace_words_in_sentence(self.welcome_mail.subject, user=new_user)

        self.assertEqual(welcome_mail.subject, welcome_mail_subject)
        self.assertEqual(welcome_mail.body, welcome_mail_html)
        self.assertEqual(welcome_mail.from_email, self.info_email)

        # Validate confirmation mail
        confirmation_mail_class = self.exportation_coffee_invitation_mail.get_mail_class()
        confirmation_mail_data = confirmation_mail_class.get_mail_template_data(new_user)
        confirmation_mail_html = get_template('survey').render(confirmation_mail_data)

        exportation_coffee_invitation_mail_subject = replace_words_in_sentence(
            self.exportation_coffee_invitation_mail.subject, user=new_user
        )

        self.assertEqual(confirmation_mail.subject, exportation_coffee_invitation_mail_subject)
        self.assertEqual(confirmation_mail.body, confirmation_mail_html)
        self.assertEqual(confirmation_mail.from_email, self.info_email)

    def test_add_already_registered_user(self):
        """
        Test add user action for a user that is already registered.
        """
        new_user = UserFactory()

        response = self.client.patch(self.add_user_url, {'email': new_user.email})

        self.assertEqual(response.status_code, HTTP_200_OK)

        new_user.refresh_from_db()
        self.assertTrue(new_user.is_active)

        new_tier = UserTier.objects.get(user=new_user)
        self.assertEqual(new_tier.tier, self.user_tier.tier)
        self.assertEqual(new_tier.valid_to, self.user_tier.valid_to)
        self.assertEqual(new_tier.parent_tier, self.user_tier)

        data = response.data

        self.assertEqual(data['id'], self.user_tier.id)
        self.assertEqual(data['user_name'], self.user.user_name)
        self.assertEqual(data['tier'], self.user_tier.tier)
        self.assertEqual(data['tier_name'], self.user_tier.tier_name)
        self.assertEqual(data['valid_to'], get_string_date(self.user_tier.valid_to))
        self.assertTrue(data['is_main_account'])
        self.assertEqual(data['beneficiaries'], self.user_tier.beneficiaries)
        self.assertIsNone(data['plan_owner'])
        self.assertEqual(data['will_renew'], self.user_tier.will_renew)
        self.assertEqual(data['available_beneficiaries_places'], self.user_tier.max_beneficiaries - 1)
        self.assertEqual(data['dispatch_time'], self.user.dispatch_time)
        self.assertEqual(data['timezone'], self.user.tzinfo)

        self.assertEqual(len(mail.outbox), 1)
        confirmation_mail = mail.outbox[0]

        mail_class = self.exportation_coffee_invitation_mail.get_mail_class()
        mail_data = mail_class.get_mail_template_data(new_user)
        html = get_template('survey').render(mail_data)

        exportation_coffee_invitation_mail_subject = replace_words_in_sentence(
            self.exportation_coffee_invitation_mail.subject, user=new_user
        )

        self.assertEqual(confirmation_mail.subject, exportation_coffee_invitation_mail_subject)
        self.assertEqual(confirmation_mail.body, html)
        self.assertEqual(confirmation_mail.from_email, self.info_email)

    def test_add_already_registered_user_for_coffee_tier(self):
        """
        Test add user action for a user that is already registered
        from a tier UserTier.TIER_TINTO
        """
        self.user_tier.tier = UserTier.TIER_TINTO
        self.user_tier.save()

        new_user = UserFactory()

        response = self.client.patch(self.add_user_url, {'email': new_user.email})

        self.assertEqual(response.status_code, HTTP_200_OK)

        data = response.data

        self.assertEqual(data['id'], self.user_tier.id)
        self.assertEqual(data['user_name'], self.user.user_name)
        self.assertEqual(data['tier'], self.user_tier.tier)
        self.assertEqual(data['tier_name'], self.user_tier.tier_name)
        self.assertEqual(data['valid_to'], get_string_date(self.user_tier.valid_to))
        self.assertTrue(data['is_main_account'])
        self.assertEqual(data['beneficiaries'], self.user_tier.beneficiaries)
        self.assertIsNone(data['plan_owner'])
        self.assertEqual(data['will_renew'], self.user_tier.will_renew)
        self.assertEqual(data['available_beneficiaries_places'], self.user_tier.max_beneficiaries - 1)
        self.assertEqual(data['dispatch_time'], self.user.dispatch_time)
        self.assertEqual(data['timezone'], self.user.tzinfo)

        self.assertEqual(len(mail.outbox), 1)
        confirmation_mail = mail.outbox[0]

        mail_class = self.tinto_invitation_mail.get_mail_class()
        mail_data = mail_class.get_mail_template_data(new_user)
        html = get_template('survey').render(mail_data)

        tinto_invitation_mail_subject = replace_words_in_sentence(
            self.tinto_invitation_mail.subject, user=new_user
        )

        self.assertEqual(confirmation_mail.subject, tinto_invitation_mail_subject)
        self.assertEqual(confirmation_mail.body, html)
        self.assertEqual(confirmation_mail.from_email, self.info_email)

    def test_remove_user_for_user_that_is_not_beneficiary(self):
        """
        Test remove user action for a user that is not beneficiary of the
        current tier.
        """
        new_user = UserFactory()

        response = self.client.patch(self.remove_user_url, {'email': new_user.email})

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Email does not correspond to any beneficiary.')

    def test_remove_user(self):
        """
        Test remove user action.
        """
        new_tier = UserTierFactory(parent_tier=self.user_tier, valid_to=self.user_tier.valid_to)

        response = self.client.patch(self.remove_user_url, {'email': new_tier.user.email})

        self.assertEqual(response.status_code, HTTP_200_OK)

        new_tier.refresh_from_db()
        self.assertEqual(new_tier.valid_to, (datetime.today() - timedelta(days=1)).date())

        data = response.data

        self.assertEqual(data['id'], self.user_tier.id)
        self.assertEqual(data['user_name'], self.user.user_name)
        self.assertEqual(data['tier'], self.user_tier.tier)
        self.assertEqual(data['tier_name'], self.user_tier.tier_name)
        self.assertEqual(data['valid_to'], get_string_date(self.user_tier.valid_to))
        self.assertTrue(data['is_main_account'])
        self.assertEqual(data['beneficiaries'], self.user_tier.beneficiaries)
        self.assertIsNone(data['plan_owner'])
        self.assertEqual(data['will_renew'], self.user_tier.will_renew)
        self.assertEqual(data['available_beneficiaries_places'], self.user_tier.max_beneficiaries)
        self.assertEqual(data['dispatch_time'], self.user.dispatch_time)
        self.assertEqual(data['timezone'], self.user.tzinfo)

        self.assertEqual(len(mail.outbox), 1)
        confirmation_mail = mail.outbox[0]

        mail_class = self.remove_beneficiary_mail.get_mail_class()
        mail_data = mail_class.get_mail_template_data(new_tier.user)
        html = get_template('survey').render(mail_data)

        remove_beneficiary_mail_subject = replace_words_in_sentence(
            self.remove_beneficiary_mail.subject, user=new_tier.user
        )

        self.assertEqual(confirmation_mail.subject, remove_beneficiary_mail_subject)
        self.assertEqual(confirmation_mail.body, html)
        self.assertEqual(confirmation_mail.from_email, self.info_email)

    def test_change_dispatch_time_with_hour_before_6_am_colombian_time(self):
        """
        Test change_dispatch_time action with an hour that is before 6 am
        colombian time.
        """
        response = self.client.patch(
            self.change_dispatch_time_url,
            {'dispatch_time': time(12, 0, 0), 'tzinfo': 'Europe/Berlin'}
        )

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['non_field_errors'][0], 'Hour must be before 6 am colombian time.')

    def test_change_dispatch_time(self):
        """
        Test change_dispatch_time action
        """
        response = self.client.patch(
            self.change_dispatch_time_url,
            {'dispatch_time': time(14, 0, 0), 'tzinfo': 'Europe/Berlin'}
        )

        self.assertEqual(response.status_code, HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.tzinfo, 'Europe/Berlin')
        self.assertEqual(self.user.dispatch_time, time(7, 0, 0))

        data = response.data

        self.assertEqual(data['id'], self.user_tier.id)
        self.assertEqual(data['user_name'], self.user.user_name)
        self.assertEqual(data['tier'], self.user_tier.tier)
        self.assertEqual(data['tier_name'], self.user_tier.tier_name)
        self.assertEqual(data['valid_to'], get_string_date(self.user_tier.valid_to))
        self.assertTrue(data['is_main_account'])
        self.assertEqual(data['beneficiaries'], self.user_tier.beneficiaries)
        self.assertIsNone(data['plan_owner'])
        self.assertEqual(data['will_renew'], self.user_tier.will_renew)
        self.assertEqual(data['available_beneficiaries_places'], self.user_tier.max_beneficiaries)
        self.assertEqual(data['dispatch_time'], time(14, 0, 0))
        self.assertEqual(data['timezone'], self.user.tzinfo)

    @patch('stripe.api_resources.subscription.Subscription.cancel')
    def test_unsuscribe(self, _):
        """
        Test unsuscribe action.
        """
        response = self.client.patch(self.unsuscribe_url)

        self.assertEqual(response.status_code, HTTP_200_OK)

        self.user_tier.refresh_from_db()
        self.assertFalse(self.user_tier.will_renew)

        self.assertEqual(len(mail.outbox), 1)
        confirmation_mail = mail.outbox[0]

        mail_class = self.unsuscribe_mail.get_mail_class()
        mail_data = mail_class.get_mail_template_data(self.user)
        html = get_template('survey').render(mail_data)

        unsuscribe_mail_subject = replace_words_in_sentence(self.remove_beneficiary_mail.subject, user=self.user)

        self.assertEqual(confirmation_mail.subject, unsuscribe_mail_subject)
        self.assertEqual(confirmation_mail.body, html)
        self.assertEqual(confirmation_mail.from_email, self.info_email)

    def test_patch_my_taste_club_for_user_with_no_valid_action(self):
        """
        Test patch my taste club info using an action that is not allowed
        """
        self.url = reverse('my_taste_club_actions', args=[self.user_tier.id, 'testing_action'])

        response = self.client.patch(self.url, {})

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['action'], 'Invalid action.')

    def test_patch_my_taste_club_for_user_with_no_tier(self):
        """
        Test patch my taste club info for user with no active tier
        """
        self.user_tier.valid_to = (datetime.now() - timedelta(days=1)).date()
        self.user_tier.save()

        response = self.client.patch(self.add_user_url, {})

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['user'], 'User has no active tier.')
