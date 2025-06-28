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

    class Meta:
        indexes = [
            models.Index(fields=['owner']),
            models.Index(fields=['is_open', 'rating']),
            models.Index(fields=['delivery_time']),
        ]

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
        # Optimized single query instead of multiple queries
        avg_price = MenuItem.objects.filter(restaurant=self).aggregate(
            avg_price=models.Avg('price')
        )['avg_price']
        return avg_price or 0
    
    def calculate_average_delivery_time(self):
        # Default delivery time calculation or return default
        return 30  # Default 30 minutes
           
        

class RestaurantAnalysis(models.Model):
    restaurant = models.OneToOneField(Restaurant, on_delete=models.CASCADE, related_name='analysis')
    
    # Cache these values to avoid repeated database hits
    _cached_stats = None
    
    def get_cached_stats(self):
        """Get all statistics in a single optimized query"""
        if self._cached_stats is None:
            from django.db.models import Count, Sum, Q
            
            # Single aggregated query for all order statistics
            order_stats = Order.objects.filter(
                restaurant=self.restaurant, 
                is_visible_to_restaurant=True
            ).aggregate(
                total_orders=Count('id'),
                total_revenue=Sum('total', filter=Q(payment_status=True)),
                total_customers=Count('user', distinct=True),
                new_orders=Count('id', filter=Q(status='Pending')),
                preparing_orders=Count('id', filter=Q(status='Preparing')),
                delivered_orders=Count('id', filter=Q(status='Delivered')),
                cancelled_orders=Count('id', filter=Q(status='Cancelled'))
            )
            
            # Menu items count
            menu_items_count = MenuItem.objects.filter(restaurant=self.restaurant).count()
            
            # Reviews stats
            review_stats = Review.objects.filter(restaurant=self.restaurant).aggregate(
                total_reviews=Count('id'),
                total_ratings=Sum('rating')
            )
            
            self._cached_stats = {
                **order_stats,
                'menu_items_count': menu_items_count,
                **review_stats
            }
            
        return self._cached_stats
    
    def total_menu_items(self):
        return self.get_cached_stats()['menu_items_count']
    
    def total_orders(self):
        return self.get_cached_stats()['total_orders'] or 0

    def total_revenue(self):
        revenue = self.get_cached_stats()['total_revenue'] or 0
        return revenue / 1000

    def total_customers(self):
        return self.get_cached_stats()['total_customers'] or 0

    def total_reviews(self):
        return self.get_cached_stats()['total_reviews'] or 0

    def total_ratings(self):
        return self.get_cached_stats()['total_ratings'] or 0
    
    def new_orders(self):
        return self.get_cached_stats()['new_orders'] or 0

    def on_delivery(self):
        return self.get_cached_stats()['preparing_orders'] or 0

    def delivered(self):
        return self.get_cached_stats()['delivered_orders'] or 0

    def canceled(self):
        return self.get_cached_stats()['cancelled_orders'] or 0

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
    category = models.ManyToManyField('Category', related_name='menu_items')
    primary_category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True, blank=True, related_name='primary_menu_items')
    menu_item_id = models.AutoField(primary_key=True)
    preparation_time = models.IntegerField(default=30)

    def __str__(self):
            menu_name = self.menu.name if self.menu else 'No Menu'
            return f'{self.name} ({menu_name})'

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categories/', null=True, blank=True)

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
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders', null=True, blank=True)
    items = models.ManyToManyField(MenuItem, related_name='orders')
    total = models.DecimalField(max_digits=6, decimal_places=2)
    order_time = models.DateTimeField(auto_now_add=True)
    delivery_person = models.ForeignKey('delivery.DeliveryPerson', on_delete=models.SET_NULL, related_name='orders', null=True, blank=True)
    delivery_address = models.CharField(max_length=100, blank=True, null=True, default='')
    is_visible_to_restaurant = models.BooleanField(default=False)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    payment_method = models.CharField(max_length=50, choices=PAYMENT_CHOICES, default='Card')
    payment_status = models.BooleanField(default=False)
    restaurant_otp_code = models.CharField(max_length=6, blank=True, null=True)
    customer_otp_code = models.CharField(max_length=6, blank=True, null=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['user', 'payment_status']),
            models.Index(fields=['restaurant', 'is_visible_to_restaurant']),
            models.Index(fields=['status']),
            models.Index(fields=['order_time']),
        ]
    
    def __str__(self):
        return f'Order {self.id} - {self.restaurant.name}'

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
        if self.restaurant_related:
            return f"{self.restaurant_related.name}'s address"
        return "Unrelated address"