from django.contrib import admin
from .models import Address, Cart, CartItem, CardDetails


admin.site.register(Address)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(CardDetails)


