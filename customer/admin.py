from django.contrib import admin
from .models import Address, Cart, CartItem


admin.site.register(Address)
admin.site.register(Cart)
admin.site.register(CartItem)


