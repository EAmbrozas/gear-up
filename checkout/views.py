from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.contrib import messages
from django.conf import settings
from profiles.models import UserProfile
from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product, ProductSize
from cart.contexts import cart_contents
import stripe
import json

def checkout(request):
    stripe_public_key = settings.STRIPE_PUBLIC_KEY
    stripe_secret_key = settings.STRIPE_SECRET_KEY

    if request.method == 'POST':
        cart = request.session.get('cart', {})
        form_data = {
            'full_name': request.POST['full_name'],
            'email': request.POST['email'],
            'phone_number': request.POST['phone_number'],
            'street_address1': request.POST['street_address1'],
            'street_address2': request.POST.get('street_address2'),
            'town_or_city': request.POST['town_or_city'],
            'county': request.POST.get('county'),
            'postcode': request.POST['postcode'],
            'country': request.POST['country'],
        }
        order_form = OrderForm(form_data)

        if order_form.is_valid():
            order = order_form.save(commit=False)
            if request.user.is_authenticated:
                order.user_profile = UserProfile.objects.get(user=request.user)
                
            pid = request.POST.get('client_secret')
            if pid:
                stripe_pid = pid.split('_secret')[0]
                order.stripe_pid = stripe_pid
            current_cart = cart_contents(request)
            order.total_cost = current_cart['total']
            order.discounted_total = current_cart.get('total_after_discount', order.total_cost)  # Set discounted total
            order.original_bag = json.dumps(cart)
            order.save()

            for item_key, item_data in cart.items():
                product_id, size = (item_key.split('-') if '-' in item_key else (item_key, None))
                product = Product.objects.get(id=product_id)
                product_size = ProductSize.objects.get(product=product, size=size) if size else None
                quantity = item_data['quantity']
                OrderLineItem.objects.create(
                    order=order,
                    product=product,
                    product_size=product_size,
                    quantity=quantity
                )

            return redirect(reverse('checkout_success', args=[order.order_number]))
        else:
            messages.error(request, 'There was an error with your form. Please double check your information.')
    else:
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                initial_data = {
                    'full_name': request.user.get_full_name(),
                    'email': request.user.email,
                    'phone_number': profile.phone_number,
                    'street_address1': profile.street_address1,
                    'street_address2': profile.street_address2,
                    'town_or_city': profile.town_or_city,
                    'county': profile.county,
                    'postcode': profile.postcode,
                    'country': profile.country,
                }
                order_form = OrderForm(initial=initial_data)
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

        current_cart = cart_contents(request)
        total = current_cart['total_after_discount']
        stripe_total = round(total * 100)
        stripe.api_key = stripe_secret_key
        intent = stripe.PaymentIntent.create(
            amount=stripe_total,
            currency=settings.STRIPE_CURRENCY,
        )

    context = {
        'order_form': order_form,
        'stripe_public_key': stripe_public_key,
        'client_secret': intent.client_secret if intent else None,
    }

    return render(request, 'checkout/checkout.html', context)

def checkout_success(request, order_number):
    """
    Handle successful checkouts
    """
    order = get_object_or_404(Order, order_number=order_number)

    messages.success(request, f'Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.')

    if 'cart' in request.session:
        del request.session['cart']
        request.session['total_quantity'] = 0

    discount_applied = order.discounted_total is not None and \
                       order.total_cost is not None and \
                       order.discounted_total < order.total_cost

    context = {
        'order': order,
        'discount_applied': discount_applied,
        'discounted_total': order.discounted_total if discount_applied else None,
    }

    return render(request, 'checkout/checkout_success.html', context)
