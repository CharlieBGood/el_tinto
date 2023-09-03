import os

import stripe

from el_tinto.integrations.stripe.models import StripePayment, StripeCustomer
from el_tinto.users.models import User
from el_tinto.utils.utils import TASTE_CLUB_PRODUCTS


def handle_payment_intent_succeeded(payment_intent):
    """
    Create StripePayment and send payment confirmation email.

    :params:
    payment_intent: stripe.PaymentIntent
    """
    stripe.api_key = os.getenv('STRIPE_KEY')

    customer_data = stripe.Customer.retrieve(payment_intent.get('customer'))

    invoice = stripe.Invoice.retrieve(payment_intent['invoice'])

    tier = TASTE_CLUB_PRODUCTS.get(invoice['lines']['data'][0]['price']['product'])

    payment = StripePayment.objects.create(
        user=User.objects.filter(email=customer_data['email']).first(),
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
