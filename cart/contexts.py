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

    for item_key, item_data in cart.items():
        product_id = item_data['product_id']
        size = item_data.get('size', None)
        quantity = item_data['quantity']
        product = Product.objects.get(pk=product_id)

        if size:
            try:
                product_size = ProductSize.objects.filter(product=product, size=size).first()
                if product_size:
                    size = product_size.size
                else:
                    size = None
            except ProductSize.DoesNotExist:
                size = None

        price = product.price
        subtotal = price * quantity
        total += subtotal
        product_count += quantity

        cart_items.append({
            'item_id': item_key,
            'quantity': quantity,
            'product': product,
            'size': size,
            'subtotal': subtotal,
        })

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
