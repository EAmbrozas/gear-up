from django.db import models
from django.contrib.auth.models import User
from products.models import Product, ProductSize
from profiles.models import UserProfile
from django_countries.fields import CountryField
from django.utils.crypto import get_random_string
from django.utils.text import slugify
import uuid

# Function to generate a unique order number
def generate_order_number():
    """
    Generate a random, unique order number using UUID
    """
    return uuid.uuid4().hex.upper()

class Order(models.Model):
    order_number = models.CharField(max_length=32, null=False, editable=False, default=generate_order_number)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    full_name = models.CharField(max_length=50, null=False, blank=False)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    street_address1 = models.CharField(max_length=80)
    street_address2 = models.CharField(max_length=80, null=True, blank=True)
    town_or_city = models.CharField(max_length=40)
    county = models.CharField(max_length=80, null=True, blank=True)
    postcode = models.CharField(max_length=20)
    country = CountryField(blank_label='Country *', null=False, blank=False)
    date = models.DateTimeField(auto_now_add=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    discounted_total = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    stripe_pid = models.CharField(max_length=254, null=True, blank=True)

    def update_total(self):
        """
        Update total cost whenever a line item is added, updated, or deleted.
        """
        self.total_cost = sum(item.lineitem_total for item in self.lineitems.all())
        self.save()

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the order number if it hasn't been set already
        """
        if not self.order_number:
            self.order_number = generate_order_number()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.order_number

class OrderLineItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='lineitems')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.IntegerField()
    lineitem_total = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)

    def save(self, *args, **kwargs):
        """
        Override the original save method to set the lineitem total and update the total_cost
        """
        self.lineitem_total = self.product.price * self.quantity
        super().save(*args, **kwargs)

        # Update the order's total cost
        total_cost = sum(item.lineitem_total for item in self.order.lineitems.all())
        self.order.total_cost = total_cost
        self.order.save()

    def __str__(self):
        return f'Item {self.product.name} on order {self.order.order_number}'
