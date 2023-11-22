from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone_number', 'town_or_city', 'county', 'postcode', 'country')
    search_fields = ('user__username', 'phone_number', 'town_or_city', 'county', 'postcode', 'country__name')
    list_filter = ('country', 'town_or_city', 'county')
    ordering = ('user',)

admin.site.register(UserProfile, UserProfileAdmin)
