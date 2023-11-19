from django.db import models
from django.utils.crypto import get_random_string
from django.utils.text import slugify

class Category(models.Model):
    name = models.CharField(max_length=254, editable=False)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.friendly_name:
            self.name = slugify(self.friendly_name).replace('-', '_')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_friendly_name(self):
        return self.friendly_name

class Brand(models.Model):
    name = models.CharField(max_length=254, editable=False)
    friendly_name = models.CharField(max_length=254, null=True, blank=True)

    def save(self, *args, **kwargs):
        if self.friendly_name:
            self.name = slugify(self.friendly_name).replace('-', '_')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.friendly_name if self.friendly_name else self.name

    def get_friendly_name(self):
        return self.friendly_name

class Product(models.Model):
    category = models.ForeignKey('Category', null=True, blank=True, on_delete=models.SET_NULL)
    brand = models.ForeignKey('Brand', null=True, blank=True, on_delete=models.SET_NULL)
    sku = models.CharField(max_length=7, unique=True, editable=False)
    name = models.CharField(max_length=254)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    rating = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    image_url = models.URLField(max_length=1024, null=True, blank=True)
    image = models.ImageField(null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.sku:
            category_initial = self.category.name[0].upper() if self.category else 'U'
            unique_number = get_random_string(length=6, allowed_chars='0123456789')
            self.sku = f"{category_initial}{unique_number}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes')
    size = models.CharField(max_length=50)
    quantity = models.PositiveIntegerField()

    def has_stock(self):
        return self.quantity > 0

    def __str__(self):
        return f"{self.product.name} - {self.size}"
