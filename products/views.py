from django.shortcuts import render, get_object_or_404, redirect
from .models import Product, Brand, Category, ProductSize  
from .forms import ProductForm, ProductSizeForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from reviews.forms import ReviewForm
from reviews.models import Review
from reviews.views import add_review
from django.db.models import Avg

def product_list(request):
    """ A view to display all products, with search and category filtering functionality """
    query = request.GET.get('q')
    category_filter = request.GET.get('category')

    if category_filter:
        products = Product.objects.filter(category__name__iexact=category_filter)
    elif query:
        products = Product.objects.filter(
            Q(name__icontains=query) |
            Q(category__name__icontains=query) |
            Q(brand__name__icontains=query)
        )
    else:
        products = Product.objects.all()

    # products = products.annotate(avg_rating=Avg('reviews__rating'))

    products_count = products.count()

    paginator = Paginator(products, 12)
    page = request.GET.get('page')
    products = paginator.get_page(page)

    brands = Brand.objects.all()
    categories = Category.objects.all()

    context = {
        'products': products,
        'brands': brands,
        'categories': categories,
        'query': query,
        'category_filter': category_filter,
        'products_count': products_count
    }

    return render(request, 'products/product_list.html', context)


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = Review.objects.filter(product=product).order_by('-created_at')

    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0

    user_review = None
    if request.user.is_authenticated:
        user_review = reviews.filter(user=request.user).first()

    if request.method == 'POST':
        if user_review:
            messages.error(request, 'You have already reviewed this product.')
            return redirect('product_detail', pk=product.pk)

        review_form = ReviewForm(request.POST)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()

            new_avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
            product.rating = new_avg_rating
            product.save()

            messages.success(request, 'Your review has been submitted successfully.')
            return redirect('product_detail', pk=product.pk)
    else:
        review_form = ReviewForm()

    context = {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'user_review': user_review,
        'num_reviews': reviews.count(),
        'avg_rating': avg_rating,
    }

    return render(request, 'products/product_detail.html', context)

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

@login_required
def add_sizes_to_product(request, pk):
    """ Add size to product """
    product = Product.objects.get(pk=pk)

    if request.method == 'POST':
        form = ProductSizeForm(request.POST)
        if form.is_valid():
            size = form.cleaned_data['size']
            quantity = form.cleaned_data['quantity']

            existing_size = ProductSize.objects.filter(product=product, size=size).first()
            
            if existing_size:
                existing_size.quantity += quantity
                existing_size.save()
                messages.success(request, f'Quantity for size {size} updated successfully.')
            else:
                product_size = ProductSize(product=product, size=size, quantity=quantity)
                product_size.save()
                messages.success(request, f'Size {size} added successfully.')

            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductSizeForm()

    return render(request, 'products/add_sizes.html', {'form': form, 'product': product})