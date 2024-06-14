from django.contrib import admin
from .models import Profile, Transaction


class ProfileAdmin(admin.ModelAdmin):
    list_display = [
        'user', 
        'phone_number', 
        'country', 
        'acct_balance', 

    ]
# Register your models here.
admin.site.register(Profile, ProfileAdmin)
admin.site.register(Transaction)