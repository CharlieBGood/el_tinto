import json
import stripe

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from el_tinto.utils.stripe import handle_payment_intent_succeeded


@csrf_exempt
@require_http_methods(["POST"])
def stripe_payment(request):
    payload = request.body

    try:
        event = stripe.Event.construct_from(
            json.loads(payload), stripe.api_key
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)

    # Handle the event
    if event.type == 'payment_intent.succeeded':
        payment_intent = event.data.object  # contains a stripe.PaymentIntent
        handle_payment_intent_succeeded(payment_intent)

    return HttpResponse(status=200)
