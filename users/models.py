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
        

class Transaction(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(decimal_places=2, max_digits=10)
    date = models.DateTimeField(auto_now_add=True)
    transaction_type = models.CharField(max_length=20)
    balance_after_transaction = models.DecimalField(decimal_places=2, max_digits=10)
    
    def __str__(self):
        return f'{self.user.username} Transaction'