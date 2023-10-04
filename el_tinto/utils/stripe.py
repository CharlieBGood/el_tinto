import os
from datetime import timedelta, date

import stripe

from el_tinto.integrations.stripe.models import StripePayment, StripeCustomer
from el_tinto.mails.models import Mail
from el_tinto.users.models import User, UserTier
from el_tinto.utils.utils import TASTE_CLUB_PRODUCTS, TASTE_CLUB_TIER_UTILS, TASTE_CLUB_OWNER_CANCELATION_MAIL, \
    TASTE_CLUB_BENEFICIARY_CANCELATION_MAIL

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
    subscription = invoice['lines']['data'][0]['subscription']

    user = User.objects.filter(email=customer_data['email']).first()

    payment = StripePayment.objects.create(
        user=user,
        amount=payment_intent['amount'],
        currency=payment_intent['currency'],
        subscription=subscription,
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
        valid_to = (date.today() + timedelta(days=30) if recurrence == 'month' else date.today() + timedelta(days=365))
        missing_sunday_mails = TASTE_CLUB_TIER_UTILS[tier]['sunday_mails']

        try:
            user_tier = UserTier.objects.get(
                user=user,
                tier=tier,
                valid_to__gte=(date.today() - timedelta(days=1))
            )

            # Update child tiers
            for child_tier in user_tier.children_tiers.filter(valid_to=user_tier.valid_to):
                child_tier.missing_sunday_mails = missing_sunday_mails
                child_tier.valid_to = valid_to
                child_tier.save()

            # Update main tier fields
            user_tier.missing_sunday_mails = missing_sunday_mails
            user_tier.valid_to = valid_to
            user_tier.save()

        except UserTier.DoesNotExist:
            user_tier = UserTier.objects.create(
                user=user,
                tier=tier,
                missing_sunday_mails=missing_sunday_mails,
                valid_to=valid_to
            )

            # send confirmation mail
            tier_mail_id = TASTE_CLUB_TIER_UTILS[tier]['welcome_mail']
            instance = Mail.objects.get(id=tier_mail_id)
            mail = instance.get_mail_class()

            mail.send_mail(user=user)

        # add payment to tier
        user_tier.payments.add(payment)


def handle_unsuscribe(user_tier):
    """
    Cancel user subscription to avoid further charging

    :params:
    user_tier: UserTier obj
    """
    try:
        subscription = user_tier.payments.all().order_by('-created').first().subscription
        stripe.Subscription.cancel(subscription)

        user_tier.will_renew = False
        user_tier.save()

        # send confirmation mail
        # send confirmation mail
        instance = Mail.objects.get(id=TASTE_CLUB_OWNER_CANCELATION_MAIL)
        mail = instance.get_mail_class()
        mail.send_mail(user=user_tier.user)

        # Update child tiers
        instance = Mail.objects.get(id=TASTE_CLUB_BENEFICIARY_CANCELATION_MAIL)
        mail = instance.get_mail_class()
        for child_tier in user_tier.children_tiers.filter(valid_to=user_tier.valid_to):
            child_tier.will_renew = False
            child_tier.save()

            # send confirmation mail
            mail.send_mail(user=child_tier.user)

    except stripe.error.InvalidRequestError:
        pass

