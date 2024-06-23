from django.db import models
from django.contrib.auth.models import User
from restaurant.models import MenuItem

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, null=True, blank=True)
    image = models.ImageField(upload_to='profile_pics', default='default.jpg')
    
    def __str__(self):
        return self.user.username


class Address(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='addresses')
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10, blank=True, null=True, default='')

    def __str__(self):
        return f'{self.user.user.username}\'s address'

class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Cart of {self.user.username}"
    
    def total_price(self):
        return sum(item.total_price() for item in self.cartitem_set.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} of {self.menu_item.name}"
    
    def total_price(self):
        return self.quantity * self.MenuItem.price