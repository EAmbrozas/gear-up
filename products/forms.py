from django import forms
from .models import Product

class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['brand', 'category', 'name', 'description', 'price', 'rating', 'image']


class ProductSizeForm(forms.Form):
    size = forms.CharField(max_length=50, label='Size')
    quantity = forms.IntegerField(label='Quantity')
