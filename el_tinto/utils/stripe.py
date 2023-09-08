import os
from datetime import datetime, timedelta

import stripe

from el_tinto.integrations.stripe.models import StripePayment, StripeCustomer
from el_tinto.users.models import User, UserTier
from el_tinto.utils.utils import TASTE_CLUB_PRODUCTS

stripe.api_key = os.getenv('STRIPE_KEY')


def handle_payment_intent_succeeded(payment_intent):
    """
    Create StripePayment and send payment confirmation email.

    :params:
    payment_intent: stripe.PaymentIntent
    """
    customer_data = stripe.Customer.retrieve(payment_intent.get('customer'))

    invoice = stripe.Invoice.retrieve(payment_intent['invoice'])

    tier = TASTE_CLUB_PRODUCTS.get(invoice['lines']['data'][0]['price']['product'])
    recurrence = invoice['lines']['data'][0]['price']['recurring']['interval']

    user = User.objects.filter(email=customer_data['email']).first()

    payment = StripePayment.objects.create(
        user=user,
        amount=payment_intent['amount'],
        currency=payment_intent['currency'],
        tier=tier,
        json=payment_intent,
    )

    StripeCustomer.objects.create(
        payment=payment,
        email=customer_data['email'],
        city=customer_data['address']['city'],
        state=customer_data['address']['state'],
        country=customer_data['address']['country'],
        address_1=customer_data['address']['line1'],
        address_2=customer_data['address']['line2'],
        postal_code=customer_data['address']['postal_code'],
        json=customer_data
    )

    if user:
        valid_to = (
            datetime.now() + timedelta(days=30) if recurrence == 'month' else datetime.now() + timedelta(days=365)
        )

        UserTier.objects.create(
            user=user,
            payment=payment,
            tier=dict(UserTier.TIERS_CHOICES).get(tier),
            valid_to=valid_to
        )
