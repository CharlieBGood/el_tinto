import uuid
from datetime import datetime, timedelta, time

from django.urls import reverse
from rest_framework.status import HTTP_200_OK, HTTP_404_NOT_FOUND
from rest_framework.test import APITestCase

from el_tinto.tests.users.factories import UserFactory, UserTierFactory
from el_tinto.users.models import UserTier
from el_tinto.utils.date_time import get_string_date
from el_tinto.utils.errors import USER_DOES_NOT_EXIST_ERROR_MESSAGE


class TestMyTasteClubView(APITestCase):

    def setUp(self):
        self.user = UserFactory(referral_code='AKIL89', tzinfo='America/Lima', dispatch_time=time(6, 0))
        self.user_tier = UserTierFactory(
            user=self.user, tier=UserTier.TIER_EXPORTATION_COFFEE,
            valid_to=datetime.today()
        )

        self.url = reverse('my_taste_club', args=[self.user.uuid])

    def test_get_my_taste_club_info(self):
        """
        Test get my taste club info for tier UserTier.TIER_EXPORTATION_COFFEE
        """
        response = self.client.get(self.url)

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
        self.assertEqual(data['available_beneficiaries_places'], self.user_tier.max_beneficiaries)
        self.assertEqual(data['dispatch_time'], self.user.dispatch_time)
        self.assertEqual(data['timezone'], self.user.tzinfo)

    def test_get_my_taste_club_info_for_tinto_tier_with_one_beneficiaries(self):
        """
        Test get my taste club info for tier UserTier.TIER_TINTO
        when one beneficiary has been added
        """
        self.user_tier.tier = UserTier.TIER_TINTO
        self.user_tier.save()

        UserTierFactory(valid_to=self.user_tier.valid_to, tier=self.user_tier.tier, parent_tier=self.user_tier)

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTP_200_OK)

        data = response.data

        self.assertEqual(data['id'], self.user_tier.id)
        self.assertEqual(data['user_name'], self.user.user_name)
        self.assertEqual(data['tier'], self.user_tier.tier)
        self.assertEqual(data['tier_name'], self.user_tier.tier_name)
        self.assertEqual(data['valid_to'], get_string_date(self.user_tier.valid_to))
        self.assertTrue(data['is_main_account'])
        self.assertEqual(len(data['beneficiaries']), 1)
        self.assertIsNone(data['plan_owner'])
        self.assertEqual(data['will_renew'], self.user_tier.will_renew)
        self.assertEqual(data['available_beneficiaries_places'], self.user_tier.max_beneficiaries - 1)
        self.assertEqual(data['dispatch_time'], self.user.dispatch_time)
        self.assertEqual(data['timezone'], self.user.tzinfo)

    def test_get_my_taste_club_info_for_beneficiary(self):
        """
        Test get my taste club info for beneficiary user
        """
        beneficiary_tier = UserTierFactory(
            valid_to=self.user_tier.valid_to, tier=self.user_tier.tier, parent_tier=self.user_tier
        )

        self.url = reverse('my_taste_club', args=[beneficiary_tier.user.uuid])

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTP_200_OK)

        data = response.data

        self.assertEqual(data['id'], beneficiary_tier.id)
        self.assertEqual(data['user_name'], beneficiary_tier.user.user_name)
        self.assertEqual(data['tier'], beneficiary_tier.tier)
        self.assertEqual(data['tier_name'], beneficiary_tier.tier_name)
        self.assertEqual(data['valid_to'], get_string_date(beneficiary_tier.valid_to))
        self.assertFalse(data['is_main_account'])
        self.assertEqual(len(data['beneficiaries']), 0)
        self.assertEqual(data['plan_owner'], self.user_tier.user.email)
        self.assertEqual(data['will_renew'], beneficiary_tier.will_renew)
        self.assertEqual(data['available_beneficiaries_places'], beneficiary_tier.max_beneficiaries)
        self.assertIsNone(data['dispatch_time'])
        self.assertEqual(data['timezone'], '')

    def test_get_my_taste_club_info_with_two_beneficiaries(self):
        """
        Test get my taste club info for tier UserTier.TIER_EXPORTATION_COFFEE
        when two beneficiaries have been added
        """
        UserTierFactory(valid_to=self.user_tier.valid_to, tier=self.user_tier.tier, parent_tier=self.user_tier)
        UserTierFactory(valid_to=self.user_tier.valid_to, tier=self.user_tier.tier, parent_tier=self.user_tier)

        response = self.client.get(self.url)

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
        self.assertEqual(data['available_beneficiaries_places'], self.user_tier.max_beneficiaries - 2)
        self.assertEqual(data['dispatch_time'], self.user.dispatch_time)
        self.assertEqual(data['timezone'], self.user.tzinfo)

    def test_get_my_taste_club_for_unexisting_user(self):
        """
        Test get my taste club info for unexisting user
        """
        self.url = reverse('my_taste_club', args=[uuid.uuid4()])
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['user'], USER_DOES_NOT_EXIST_ERROR_MESSAGE)

    def test_get_my_taste_club_for_user_with_no_tier(self):
        """
        Test get my taste club info for user with no active tier
        """
        self.user_tier.valid_to = (datetime.now() - timedelta(days=1)).date()
        self.user_tier.save()

        response = self.client.get(self.url)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['user'], 'User has no active tier.')
