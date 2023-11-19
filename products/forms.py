from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['brand', 'category', 'name', 'description', 'price', 'rating', 'image']

