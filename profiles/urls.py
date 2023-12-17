from django.urls import path
from . import views
from .views import order_detail_view 

urlpatterns = [
    path('profile/', views.profile_detail, name='profile_detail'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('order/<str:order_number>/', order_detail_view, name='order_detail'),
]
