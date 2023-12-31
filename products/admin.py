from django.contrib import admin
from .models import Category, Brand, Product, ProductSize

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('friendly_name', 'name')
    search_fields = ('friendly_name', 'name')

@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('friendly_name', 'name')
    search_fields = ('friendly_name', 'name')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'sku', 'price', 'rating', 'image')
    readonly_fields = ('sku',)
    list_filter = ('brand', 'category', 'rating')
    search_fields = ('name', 'description', 'sku', 'brand__name')
    exclude = ('sku',)  # Exclude from form

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'quantity')
    list_filter = ('product',)
    search_fields = ('product__name', 'size')

