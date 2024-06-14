from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    acct_balance = models.DecimalField(default=0, decimal_places=2, max_digits=10, blank=True) 
    date_created = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.user.username} Profile'

    def save(self, *args, **kwargs):
        request = kwargs.pop('request', None)  # Retrieve the request object from kwargs

class Address(models.Model):
    TYPE_CHOICES = [
        ('Home', 'Home'),
        ('Work', 'Work'),
    ]

    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    
    def __str__(self):
        return f"{self.type} - {self.address}"
    
    
class Category(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='categories/')

    def __str__(self):
        return self.name
    
    
class Product(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='products/')
    rating = models.DecimalField(max_digits=2, decimal_places=1)
    reviews_count = models.IntegerField()

    def __str__(self):
        return self.name

class Order(models.Model):
    customer = models.ForeignKey('auth.User', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Order {self.id} by {self.customer}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} of {self.product.name}"