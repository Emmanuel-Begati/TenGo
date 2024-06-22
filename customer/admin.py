from django.contrib import admin
from .models import Order, UserProfile, Address


admin.site.register(Order)
admin.site.register(UserProfile)
admin.site.register(Address)


