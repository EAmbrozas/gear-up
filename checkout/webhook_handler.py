from django.http import HttpResponse
from .models import Order, OrderLineItem
from products.models import Product
from django.contrib import messages
from django.db import transaction
import json
import time

class StripeWH_Handler:
    """Handle Stripe webhooks"""

    def __init__(self, request):
        self.request = request

    def handle_event(self, event):
        """
        Handle a generic/unknown/unexpected webhook event
        """
        return HttpResponse(
            content=f'Unhandled webhook received: {event["type"]}',
            status=200)

    def handle_payment_intent_succeeded(self, event):
        """
        Handle the payment_intent.succeeded webhook from Stripe
        """
        intent = event.data.object  # The Stripe Payment Intent
        pid = intent.id
        cart = json.loads(intent.metadata.cart)

        billing_details = intent.charges.data[0].billing_details
        shipping_details = intent.shipping
        total = round(intent.charges.data[0].amount / 100, 2)

        for field, value in shipping_details.address.items():
            if value == "":
                shipping_details.address[field] = None

        order_exists = False
        attempt = 1
        while attempt <= 5:
            try:
                order = Order.objects.get(stripe_pid=pid)
                order_exists = True
                break
            except Order.DoesNotExist:
                attempt += 1
                time.sleep(1)
        
        if order_exists:
            return HttpResponse(content=f'Webhook received: {event["type"]} | SUCCESS: Verified order already in database', status=200)
        else:
            # Create order if it doesn't exist
            order = self._create_order(intent, billing_details, shipping_details, cart, pid, total)
            if order:
                return HttpResponse(content=f'Webhook received: {event["type"]} | SUCCESS: Created order in webhook', status=200)
            else:
                return HttpResponse(content=f'Webhook received: {event["type"]} | ERROR: Could not create order', status=500)

    def handle_payment_intent_payment_failed(self, event):
        """
        Handle the payment_intent.payment_failed webhook from Stripe
        """
        return HttpResponse(content=f'Webhook received: {event["type"]}', status=200)

    def _create_order(self, request, intent, billing_details, shipping_details, cart, pid, total):
        """
        Create an order based on the webhook data.
        """
        try:
            with transaction.atomic():
                order = Order.objects.create(
                    full_name=shipping_details.name,
                    email=billing_details.email,
                    phone_number=shipping_details.phone,
                    street_address1=shipping_details.address.line1,
                    street_address2=shipping_details.address.line2,
                    town_or_city=shipping_details.address.city,
                    county=shipping_details.address.state,
                    postcode=shipping_details.address.postal_code,
                    country=shipping_details.address.country,
                    total_cost=total,
                    stripe_pid=pid,
                )

                for item_id, quantity in cart.items():
                    product = Product.objects.get(id=item_id)
                    OrderLineItem.objects.create(
                        order=order,
                        product=product,
                        quantity=quantity
                    )
            return order
        except Product.DoesNotExist:
            # Inform the user if a product in the cart was not found in the database
            messages.error(request, "One of the products in your cart was not found. Please contact support for assistance.")
            transaction.rollback()
            return None
        except Exception as e:
            # Inform the user of a generic error
            messages.error(request, "An error occurred while processing your order. Please try again.")
            transaction.rollback()
            return None