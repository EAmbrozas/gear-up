from django.conf import settings
from decimal import Decimal
from products.models import Product, ProductSize

def cart_contents(request):
    """
    Context processor to make cart contents and discount available across all templates.
    """
    cart_items = []
    total = Decimal('0.0')
    product_count = 0
    cart = request.session.get('cart', {})
    discount = Decimal('0.0')

    for item_key, item_data in cart.copy().items():
        product_id = item_data['product_id']
        size = item_data.get('size', None)
        quantity = item_data['quantity']

        try:
            product = Product.objects.get(pk=product_id)
        except Product.DoesNotExist:
            cart.pop(item_key)
            continue

        product_size = None
        if size:
            product_size = ProductSize.objects.filter(product=product, size=size).first()
            if not product_size:
                size = None

        price = product.price
        subtotal = price * quantity
        total += subtotal
        product_count += quantity

        cart_items.append({
            'item_id': item_key,
            'quantity': quantity,
            'product': product,
            'size': size if product_size else None,
            'subtotal': subtotal,
        })

    if request.user.is_authenticated:
        discount = total * Decimal('0.1')
        total_after_discount = total - discount
    else:
        total_after_discount = total

    request.session['cart'] = cart  # Update the session cart
    return {
        'cart_items': cart_items,
        'total': total,
        'product_count': product_count,
        'discount': discount,
        'total_after_discount': total_after_discount,
    }
