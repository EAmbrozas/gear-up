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

    for item_key, quantity in cart.items():
        item_parts = item_key.split('-')
        product_id = item_parts[0]
        size_id = item_parts[1] if len(item_parts) > 1 else None
        product = Product.objects.get(pk=product_id)

        if size_id:
            try:
                size_id = int(size_id)
                size = ProductSize.objects.get(pk=size_id)
            except ValueError:
                continue

            price = product.price
            subtotal = price * quantity
            cart_items.append({
                'item_id': item_key,
                'quantity': quantity,
                'product': product,
                'size': size,
                'subtotal': subtotal,
            })
        else:
            price = product.price
            subtotal = price * quantity
            cart_items.append({
                'item_id': item_key,
                'quantity': quantity,
                'product': product,
                'subtotal': subtotal,
            })

        total += subtotal
        product_count += quantity

    if request.user.is_authenticated:
        discount = total * Decimal('0.1')
        total_after_discount = total - discount
    else:
        total_after_discount = total

    return {
        'cart_items': cart_items,
        'total': total,
        'product_count': product_count,
        'discount': discount,
        'total_after_discount': total_after_discount,
    }
