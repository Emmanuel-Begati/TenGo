from django.contrib import admin
from customer.models import Customer, Address, Card, Order

# Register your models here.
admin.site.register(Customer)
admin.site.register(Address)
admin.site.register(Card)
admin.site.register(Order)