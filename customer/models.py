from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.contrib.auth.models import User



class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(blank=True)
    birth_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.user.username

class MenuItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    image = models.ImageField(upload_to='menu_images')
    price = models.DecimalField(max_digits=6, decimal_places=2)
    category = models.ManyToManyField('Category', related_name='item')
    
    def __str__(self):
        return self.name
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name
    
class Order(models.Model):
    items = models.ManyToManyField('MenuItem', related_name='order', blank=True)
    customer_name = models.CharField(max_length=100)
    customer_address = models.TextField()
    customer_phone = models.CharField(max_length=20)
    total = models.DecimalField(max_digits=6, decimal_places=2)
    order_time = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Order: {self.order_time.strftime("%Y-%m-%d %H:%M")}'


    

class Address(models.Model):
    user = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='user_address')
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    zip = models.CharField(max_length=10)
    
    def __str__(self):
        return f'{self.user.username}\'s address'