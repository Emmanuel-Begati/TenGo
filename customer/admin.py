from django.contrib import admin
from .models import UserProfile, Address, Cart, CartItem


admin.site.register(UserProfile)
admin.site.register(Address)
admin.site.register(Cart)
admin.site.register(CartItem)


