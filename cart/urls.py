from django.urls import path
from .views import add_to_cart, view_cart, adjust_cart, remove_from_cart

urlpatterns = [
    path('add/<int:pk>/', add_to_cart, name='add_to_cart'),
    path('view/', view_cart, name='view_cart'),
    path('adjust/<int:pk>/', adjust_cart, name='adjust_cart'),
    path('remove/<int:pk>/', remove_from_cart, name='remove_from_cart'),
]
