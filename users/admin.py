from django.contrib import admin
from .models import Profile, Address, Category, Product, Order, OrderItem


class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 
        'phone_number', 
        'country', 
        'acct_balance', 

    ]
# Register your models here.
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Address)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)