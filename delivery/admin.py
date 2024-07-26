from django.contrib import admin
from .models import DeliveryPerson, Delivery

# Register your models here.
admin.site.register(DeliveryPerson)
admin.site.register(Delivery)