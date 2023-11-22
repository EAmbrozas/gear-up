from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_detail, name='profile_detail'),
    path('profile/update/', views.profile_update, name='profile_update'),
]
