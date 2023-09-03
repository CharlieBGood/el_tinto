from django.urls import path

from el_tinto.integrations.stripe.views import stripe_payment

urlpatterns = [
    path('stripe/payment/', stripe_payment, name='stripe'),
]
