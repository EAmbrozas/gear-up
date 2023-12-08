from django.shortcuts import render, redirect, reverse
from django.contrib import messages
from .forms import OrderForm
from cart.contexts import cart_contents  # Import the cart_contents function

def checkout(request):
    # Debugging: Print the current session cart
    print("Session Cart:", request.session.get('cart', {}))

    cart = request.session.get('cart', {})
    if not cart:
        messages.error(request, "There's nothing in your cart at the moment")
        return redirect(reverse('product_list'))

    order_form = OrderForm()
    
    # Manually get cart contents
    cart_context = cart_contents(request)

    # Debugging: Print the cart context
    print("Cart Context:", cart_context)

    template = 'checkout/checkout.html'
    context = {
        'order_form': order_form,
        'cart_items': cart_context['cart_items'],  # Add cart items to context
        'total_after_discount': cart_context['total_after_discount'],  # Add total after discount to context
    }

    # Debugging: Print the final context being passed to the template
    print("Context being passed to template:", context)

    return render(request, template, context)
