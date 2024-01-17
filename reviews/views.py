import logging
from django.shortcuts import render, redirect, get_object_or_404
from .forms import ReviewForm
from reviews.models import Review
from products.models import Product
from django.contrib import messages
from django.contrib.auth.decorators import login_required

@login_required
def add_review(request, pk):
    logger = logging.getLogger(__name__)
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        review_form = ReviewForm(request.POST, request.FILES)
        if review_form.is_valid():
            review = review_form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()

            product.update_rating()

            logger.info('Review successfully created')
            messages.success(request, 'Review successfully created!')
            return redirect('product_detail', pk=pk)
        else:
            logger.error('Form is not valid')
            messages.error(request, 'Failed to create review. Please ensure the form is valid.')
    else:
        review_form = ReviewForm()

    context = {
        'review_form': review_form,
        'product': product,
    }

    return render(request, 'product_detail.html', context)
