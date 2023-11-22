from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from products.models import Product, ProductSize
from decimal import Decimal

def view_cart(request):
    """
    A view that renders the cart contents page.
    Calculates the total price of items in the cart and applies a 10% discount for authenticated users.
    """
    cart_items = []
    total = Decimal('0.0')
    product_count = 0
    total_quantity = 0
    cart = request.session.get('cart', {})
    discount = Decimal('0.0')

    for item_key, item_data in cart.items():
        item_parts = item_key.split('-')
        pk = item_parts[0]
        size = item_parts[1] if len(item_parts) > 1 else None
        product = get_object_or_404(Product, pk=pk)

        quantity = item_data.get('quantity', 0)
        subtotal = product.price * quantity
        total += Decimal(subtotal)
        product_count += quantity
        total_quantity += quantity

        cart_items.append({
            'item_id': pk,
            'quantity': quantity,
            'product': product,
            'size': size,
            'subtotal': subtotal,
        })

    request.session['total_quantity'] = total_quantity

    if request.user.is_authenticated:
        discount = total * Decimal('0.1')  # 10% discount

    total_after_discount = total - discount

    context = {
        'cart_items': cart_items,
        'total': total,
        'product_count': product_count,
        'total_quantity': total_quantity,
        'discount': discount,
        'total_after_discount': total_after_discount,
    }

    return render(request, 'cart/cart.html', context)

def add_to_cart(request, pk):
     """
    Add a quantity of the specified product to the shopping cart.
    Checks product availability in the selected size and updates the cart accordingly.
    """
    product = get_object_or_404(Product, pk=pk)
    quantity = int(request.POST.get('quantity'))
    size = request.POST.get('product_size', None)
    cart = request.session.get('cart', {})

    if product.sizes.all().exists() and size:
        product_size = get_object_or_404(ProductSize, product=product, size=size)
        if product_size.quantity < quantity:
            messages.error(request, f'Sorry, there is not enough stock available in size {size}.')
            return redirect('product_detail', pk=pk)

    item_key = str(pk) + ('-' + str(size) if size else '')

    if item_key in cart:
        cart[item_key]['quantity'] += quantity
    else:
        cart[item_key] = {
            'quantity': quantity,
            'product_id': pk,
            'size': size
        }

    request.session['cart'] = cart
    total_quantity = sum(item['quantity'] for item in cart.values())
    request.session['total_quantity'] = total_quantity
    
    success_message = f'Added {product.name} to your cart'
    if size:
        success_message += f' in size {size}'
    success_message += f' (Quantity: {quantity}).'
    messages.success(request, success_message)
    
    return redirect('product_detail', pk=pk)

def adjust_cart(request, pk):
    """
    Adjust the quantity of the specified product in the shopping cart.
    Validates product availability in the selected size or stock and updates the cart.
    """
    product = get_object_or_404(Product, pk=pk)
    quantity = int(request.POST.get('quantity'))
    size = request.POST.get('product_size', None)
    cart = request.session.get('cart', {})

    item_key = str(pk) + ('-' + str(size) if size else '')

    if size:
        product_size = get_object_or_404(ProductSize, product=product, size=size)
        if quantity > product_size.quantity:
            messages.error(request, "Sorry, we don't have enough stock available.")
            return redirect('view_cart')
    elif quantity > product.stock:
        messages.error(request, "Sorry, we don't have enough stock available.")
        return redirect('view_cart')

    if quantity > 0:
        cart[item_key]['quantity'] = quantity
    else:
        del cart[item_key]

    request.session['cart'] = cart
    return redirect('view_cart')

def remove_from_cart(request, pk):
    """
    Remove the item from the shopping cart.
    Handles the removal of items from the cart based on the product and size.
    """
    try:
        size = request.POST.get('product_size', None)
        cart = request.session.get('cart', {})

        item_key = str(pk) + ('-' + str(size) if size else '')
        del cart[item_key]

        request.session['cart'] = cart
        messages.success(request, 'Item removed from your cart')
        return redirect('view_cart')
    except Exception as e:
        messages.error(request, f'Error removing item: {e}')
        return redirect('view_cart')
