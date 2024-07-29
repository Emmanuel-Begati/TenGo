# restaurant/models.py
from django.db import models
from django.conf import settings  # Updated to use settings.AUTH_USER_MODEL
from user.models import User
from django.db.models import Count, Sum

# from customer.models import Cart

class Restaurant(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    address = models.ForeignKey('RestaurantAddress', on_delete=models.SET_NULL, null=True, related_name='restaurants', blank=True)
    phone = models.CharField(max_length=20)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='restaurants', null=True, blank=True)
    image = models.ImageField(upload_to='restaurants/', null=True, blank=True)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    delivery_time = models.IntegerField(default=30)
    is_open = models.BooleanField(default=True)
    average_cost = models.DecimalField(max_digits=6, decimal_places=2, default=0)

    def __str__(self):
        return self.name
    
    def total_menu_items(self):
        return self.menu_items.count()
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if not self.address:
            # If the address field is not set, try to find a related RestaurantAddress
            related_address = RestaurantAddress.objects.filter(restaurant_related=self).first()
            if related_address:
                self.address = related_address
                
        if not self.average_cost:
            self.average_cost = self.calculate_average_cost()
        
        if not self.delivery_time:
            self.delivery_time = self.calculate_average_delivery_time()
                    
    def calculate_average_cost(self):
        total_menu_items = self.total_menu_items()
        if total_menu_items == 0:
            return 0  # Return 0 or any default value you see fit when there are no menu items
        total = 0
        for menu in self.menus.all():
            for item in menu.menu_items.all():
                total += item.price
        return total / total_menu_items
           
        

class RestaurantAnalysis(models.Model):
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, related_name='analysis')
    def total_menu_items(self):
        menus = Menu.objects.filter(restaurant=self.restaurant)
        return MenuItem.objects.filter(menu__in=menus).count()
    
    def total_orders(self):
        return Order.objects.filter(restaurant=self.restaurant, is_visible_to_restaurant=True).count()

    def total_revenue(self):
        total_sum = Order.objects.filter(restaurant=self.restaurant, payment_status=True, is_visible_to_restaurant=True).aggregate(Sum('total'))['total__sum']
        return (total_sum or 0) / 1000

    def total_customers(self):
        return Order.objects.filter(restaurant=self.restaurant, is_visible_to_restaurant=True).values('user').distinct().count() or 0

    def total_reviews(self):
        return Review.objects.filter(restaurant=self.restaurant).count()

    def total_ratings(self):
        return Review.objects.filter(restaurant=self.restaurant).aggregate(Sum('rating'))['rating__sum'] or 0
    
    def new_orders(self):
        return Order.objects.filter(restaurant=self.restaurant, status='Pending', is_visible_to_restaurant=True).count()

    def on_delivery(self):
        return Order.objects.filter(restaurant=self.restaurant, status='Preparing', is_visible_to_restaurant=True).count()

    def delivered(self):
        return Order.objects.filter(restaurant=self.restaurant, status='Delivered', is_visible_to_restaurant=True).count()

    def canceled(self):
        return Order.objects.filter(restaurant=self.restaurant, status='Cancelled', is_visible_to_restaurant=True).count()

    def __str__(self):
        return f'Analysis for {self.restaurant.name}'

    def __str__(self):
        return f'Analysis for {self.restaurant.name}'


class Menu(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menus', null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    
    def save(self, *args, **kwargs):
        if not self.name:  # Check if name is not set
            self.name = f'{self.restaurant.name} Menu'  # Set default name
        super(Menu, self).save(*args, **kwargs)  # Call the "real" save() method.

    def __str__(self):
        return f'{self.name} - {self.restaurant.name}'

class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items', null=True, blank=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE, related_name='menu_items', null=True, blank=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_items/')
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, related_name='menu_items')
    menu_item_id = models.AutoField(primary_key=True)
    preparation_time = models.IntegerField(default=30)

    def __str__(self):
            menu_name = self.menu.name if self.menu else 'No Menu'
            return f'{self.name} ({menu_name})'

class Category(models.Model):
    name = models.CharField(max_length=100)
    # image = models.ImageField(upload_to='categories/', null=True, blank=True)

    def __str__(self):
        return self.name

class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews', null=True, blank=True)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Review by {self.user.email} for {self.restaurant.name}'

class Order(models.Model):
    STATUS_CHOICES=[
        ('Pending', 'Pending'),
        ('Preparing', 'Preparing'),
        ('Out for delivery', 'Out for delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
        ('Ready for Delivery', 'Ready for Delivery'),
    ]
    PAYMENT_CHOICES=[
        ('Cash', 'Cash'),
        ('Card', 'Card'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    reference = models.CharField(max_length=100, unique=True, blank=True, null=True)
    payment_status = models.BooleanField(default=False)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    items = models.ManyToManyField(MenuItem, related_name='orders')
    total = models.DecimalField(max_digits=6, decimal_places=2)
    order_time = models.DateTimeField(auto_now_add=True)
    delivery_person = models.ForeignKey('delivery.DeliveryPerson', on_delete=models.SET_NULL, related_name='orders', null=True, blank=True)
    delivery_address = models.CharField(max_length=100, blank=True, null=True, default='')
    is_visible_to_restaurant = models.BooleanField(default=False)  # New field
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default='Card')
    payment_status = models.BooleanField(default=False)
    restaurant_otp_code = models.CharField(max_length=6, blank=True, null=True)
    customer_otp_code = models.CharField(max_length=6, blank=True, null=True)
    
    def __str__(self):
        return f'Order {self.id} - {self.restaurant.name}'
    
    def calculate_total(self):
        total = 0
        for item in self.items.all():
            total += item.price
        return total
    
    def create_restaurant_otp(self):
        import random
        self.restaurant_otp_code = ''.join(random.choices('0123456789', k=6))
    
    def create_customer_otp(self):
        import random
        self.customer_otp_code = ''.join(random.choices('0123456789', k=6))
    
    def save(self, *args, **kwargs):
        if not self.pk:  # Check if the order is being created for the first time
            self.create_restaurant_otp()
            self.create_customer_otp()
        super().save(*args, **kwargs)
        

class RestaurantAddress(models.Model):
    restaurant_related = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='restaurant_addresses', null=True, blank=True)
    country = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    street = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10, blank=True, null=True, default='')

    def __str__(self):
        return f"{self.restaurant_related.name}'s address"