from django.contrib import admin
from .models import Order, OrderLineItem

class OrderLineItemAdminInline(admin.TabularInline):
    model = OrderLineItem
    readonly_fields = ('lineitem_total',)

class OrderAdmin(admin.ModelAdmin):
    inlines = (OrderLineItemAdminInline,)

    readonly_fields = ('order_number', 'date', 'total_cost', 'stripe_pid')

    fields = ('order_number', 'user_profile', 'full_name', 'email', 'phone_number', 
              'street_address1', 'street_address2', 'town_or_city', 'county', 
              'postcode', 'country', 'date', 'total_cost')

    list_display = ('order_number', 'date', 'full_name', 'total_cost')

    ordering = ('-date',)

admin.site.register(Order, OrderAdmin)
