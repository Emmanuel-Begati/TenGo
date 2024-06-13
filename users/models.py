from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()
# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(default='default.jpg', upload_to='profile_pics')
    phone_number = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    acct_balance = models.DecimalField(default=0, decimal_places=2, max_digits=10, blank=True) 
    date_created = models.DateTimeField(auto_now_add=True)
    