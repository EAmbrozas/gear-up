from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import OrderForm
from cart.contexts import cart_contents
from django.conf import settings

def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "There's nothing in your cart at the moment")
        return redirect(reverse('product_list'))

    order_form = OrderForm()
    
    cart_context = cart_contents(request)

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'cart_items': cart_context['cart_items'],
        'total_after_discount': cart_context['total_after_discount'],
        'stripe_public_key': settings.STRIPE_PUBLIC_KEY,
    }

    return render(request, template, context)
