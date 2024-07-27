from django.db import models
from django.conf import settings
from restaurant.models import Order

class DeliveryPerson(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, )
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    vehicle_number = models.CharField(max_length=20, blank=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return self.user.first_name

class Delivery(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    delivery_person = models.ForeignKey(DeliveryPerson, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('accepted', 'Accepted'), ('delivered', 'Delivered')], default='pending')
    accepted_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.order.id} - {self.status}"