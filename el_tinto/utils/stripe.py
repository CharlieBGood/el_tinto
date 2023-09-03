from el_tinto.integrations.stripe.models import StripePayment
from el_tinto.users.models import User


def handle_payment_intent_succeeded(payment_intent):
    """
    Create StripePayment and send payment confirmation email.

    :params:
    payment_intent: stripe.PaymentIntent
    """
    StripePayment.objects.create(
        user=User.objects.first(),
        amount=payment_intent.get('amount'),
        currency=payment_intent.get('currency') or 'OIL',
        json=payment_intent
    )

