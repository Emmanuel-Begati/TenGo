# customer/models.py
from django.db import models
from django.conf import settings
from restaurant.models import MenuItem
from user.models import User

class Address(models.Model):
    CHOICES = (
        ('Home', 'Home'),
        ('Work', 'Work'),
        ('Other', 'Other'),
    )
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='customer_addresses', null=True, blank=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10, blank=True, null=True, default='')
    type = models.CharField(max_length=10, choices=CHOICES, default='Home')

    def __str__(self):
        return f'{self.customer.first_name}\'s address'


class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # Automatically updates to current time when object is saved
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')

    def __str__(self):
        return f"Cart of {self.user.email}"
    
    def total_price(self):
        return sum(item.total_price() for item in self.cart_items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='cart_items', on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Assuming price is a decimal

    def __str__(self):
        return f"{self.quantity} of {self.menu_item.name} at {self.price} each"

    def total_price(self):
        return self.quantity * self.price  # Use the stored price instead of the menu item's current price