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

    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='stripe_payments')
    tier = models.SmallIntegerField(default=TIER_COFFEE_SEED, choices=TIERS_CHOICES)
    amount = models.PositiveSmallIntegerField(help_text='Amount of payment')
    currency = models.CharField(max_length=3, help_text='Currency of payment')
    json = models.JSONField()
