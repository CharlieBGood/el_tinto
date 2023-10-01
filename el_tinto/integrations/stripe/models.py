from django.db import models


class StripePayment(models.Model):
    user = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='stripe_payments', null=True)
    amount = models.PositiveIntegerField(help_text='Amount of payment in cents')
    currency = models.CharField(max_length=3, help_text='Currency of payment')
    user_tier = models.ForeignKey('users.UserTier', on_delete=models.CASCADE, related_name='payments', null=True)
    subscription = models.CharField(max_length=40, default='', help_text='Subscription related to payment')
    created = models.DateField(auto_now_add=True)
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
