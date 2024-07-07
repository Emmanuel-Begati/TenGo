# restaurant/models.py
from django.db import models
from django.conf import settings  # Updated to use settings.AUTH_USER_MODEL
from user.models import User
# from customer.models import Cart

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.ForeignKey('Address', on_delete=models.SET_NULL, null=True, related_name='restaurants', blank=True)  # Added line
    phone = models.CharField(max_length=20)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='restaurants')
    image = models.ImageField(upload_to='restaurants/', null=True, blank=True)
    

    def __str__(self):
        return self.name

class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menus')
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def save(self, *args, **kwargs):
        if not self.name:  # Check if name is not set
            self.name = f'{self.restaurant.name} Menu'  # Set default name
        super(Menu, self).save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        return f'{self.name} - {self.restaurant.name}'

class MenuItem(models.Model):
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='menu_items')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/')
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name='menu_items')
    menu_item_id = models.AutoField(primary_key=True)

    def __str__(self):
        return f'{self.name} ({self.menu.name})'

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.email} for {self.restaurant.name}'

class DeliveryPerson(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='delivery_person')
    phone = models.CharField(max_length=20)
    vehicle_details = models.TextField()
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.user.email} (Delivery Person)'

class Delivery(models.Model):
    order = models.OneToOneField('Order', on_delete=models.CASCADE, related_name='delivery')
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

class Order(models.Model):
    STATUS_CHOICES=[
        ('Pending', 'Pending'),
        ('Preparing', 'Preparing'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    items = models.ManyToManyField(MenuItem, related_name='orders')
    total = models.DecimalField(max_digits=6, decimal_places=2)
    order_time = models.DateTimeField(auto_now_add=True)
    delivery_address = models.ForeignKey('customer.Address', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, choices=[
        ('Pending', 'Pending'),
        ('Preparing', 'Preparing'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ], default='Pending')
    quantity = models.PositiveIntegerField(default=0)
    
    def save(self, *args, **kwargs):
        quantity = 0
        for item in self.items.all():
            quantity += 1
        self.quantity = quantity
        
        
    def __str__(self):
        return f'Order {self.id} - {self.restaurant.name}'
    
    def calculate_total(self):
        total = 0
        for item in self.items.all():
            total += item.price
        return total

class Address(models.Model):
    restaurant_related = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='restaurant_addresses', null=True, blank=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10, blank=True, null=True, default='')

    def __str__(self):
        return f'{self.restaurant_related.name}\'s address'