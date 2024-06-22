from django.contrib import admin
from django.contrib import admin
from .models import Restaurant, Menu, MenuItem, Category, Order, Review, DeliveryPerson, Delivery

admin.site.register(Restaurant)
admin.site.register(Menu)
admin.site.register(MenuItem)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(DeliveryPerson)
admin.site.register(Delivery)
