from django.db import models
from django.conf import settings  # Updated to use settings.AUTH_USER_MODEL

# Create your models here.
class DeliveryPerson(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='delivery_person', null=True, blank=True)
    phone = models.CharField(max_length=20)
    vehicle_details = models.TextField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.email} (Delivery Person)'

class Delivery(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='delivery', null=True, blank=True)
    delivery_person = models.ForeignKey(DeliveryPerson, on_delete=models.SET_NULL, null=True, related_name='deliveries')
    delivery_time = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=50, choices=[
        ('Pending', 'Pending'),
        ('Picked Up', 'Picked Up'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ], default='Pending')

    def __str__(self):
        return f'Delivery for Order {self.order.id}'
