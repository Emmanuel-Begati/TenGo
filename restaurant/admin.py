from django.contrib import admin
from django.contrib import admin
from .models import Restaurant, MenuItem, Category, Order, Review,  RestaurantAddress, RestaurantAnalysis

admin.site.register(Restaurant)
admin.site.register(MenuItem)
admin.site.register(Category)
admin.site.register(Order)
admin.site.register(Review)
admin.site.register(RestaurantAddress)
admin.site.register(RestaurantAnalysis)