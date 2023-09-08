from django.db import models


class StripePayment(models.Model):
    TIER_COFFEE_SEED = 1
    TIER_COFFEE_BEAN = 2
    TIER_TINTO = 3
    TIER_EXPORTATION_COFFEE = 4

    TIERS_CHOICES = (
        (TIER_COFFEE_SEED, 'Semilla de café'),
        (TIER_COFFEE_BEAN, 'Grano de café'),
        (TIER_TINTO, 'Tinto'),
        (TIER_EXPORTATION_COFFEE, 'Café de exportación')
    )

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='stripe_payments', null=True)
    tier = models.SmallIntegerField(default=TIER_COFFEE_SEED, choices=TIERS_CHOICES)
    amount = models.PositiveSmallIntegerField(help_text='Amount of payment in cents')
    currency = models.CharField(max_length=3, help_text='Currency of payment')
    json = models.JSONField()


class StripeCustomer(models.Model):
    payment = models.OneToOneField('stripe.StripePayment', on_delete=models.CASCADE)
    email = models.EmailField()
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=50, blank=True, null=True)
    country = models.CharField(max_length=4, blank=True, null=True)
    address_1 = models.CharField(max_length=128, blank=True, null=True)
    address_2 = models.CharField(max_length=128, blank=True, null=True)
    postal_code = models.CharField(max_length=10, blank=True, null=True)
    json = models.JSONField()