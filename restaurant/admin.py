from django.contrib import admin
from .models import Restaurant, MenuItem, Order, OrderItem
# Register your models here.

admin.site.register(Restaurant)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(OrderItem)
