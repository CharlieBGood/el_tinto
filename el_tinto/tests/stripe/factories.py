import factory

from el_tinto.integrations.stripe.models import StripePayment
from el_tinto.tests.users.factories import UserFactory, UserTierFactory


class StripePaymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = StripePayment

    user = factory.SubFactory(UserFactory)
    amount = 5000000
    currency = 'COP'
    user_tier = factory.SubFactory(UserTierFactory)
    json = {}
