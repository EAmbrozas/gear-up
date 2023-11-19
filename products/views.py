from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Brand, Category
from .forms import ProductForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q

def product_list(request):
    """ A view to display all products, with search functionality """
    query = request.GET.get('q')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query) | 
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query)
        )
    else:
        products = Product.objects.all()

    brands = Brand.objects.all()
    categories = Category.objects.all()

    return render(request, 'products/product_list.html', {'products': products, 'brands': brands, 'categories': categories})


def product_detail(request, pk):
    """ A view to display individual product details """
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'products/product_detail.html', {'product': product})

@login_required
def product_create(request):
    """ Add a product to the store """
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product successfully created!')
            return redirect('product_list')
        else:
            messages.error(request, 'Failed to create product. Please ensure the form is valid.')
    else:
        form = ProductForm()
    return render(request, 'products/product_create.html', {'form': form})

@login_required
def product_update(request, pk):
    """ Edit a product in the store """
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Product successfully updated!')
            return redirect('product_detail', pk=product.pk)
        else:
            messages.error(request, 'Failed to update product. Please ensure the form is valid.')
    else:
        form = ProductForm(instance=product)
        messages.info(request, f'You are editing {product.name}.')

    return render(request, 'products/product_update.html', {'form': form, 'product': product})

@login_required
def product_delete(request, pk):
    """ Delete a product from the store """
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        product.delete()
        messages.success(request, 'Product successfully deleted!')
        return redirect('product_list')
    else:
        messages.warning(request, 'Are you sure you want to delete this product?')
    return render(request, 'products/product_delete.html', {'product': product})
