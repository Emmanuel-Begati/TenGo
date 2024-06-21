from django.contrib import admin
from .models import MenuItem, Category, Order, UserProfile, Address

admin.site.register(MenuItem)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(UserProfile)
admin.site.register(Address)


