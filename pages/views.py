from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'pages/index.html')

@login_required
def location(request):
    return render(request, 'pages/location.html')

@login_required
def landing(request):
    return render(request, 'pages/landing.html')

@login_required
def food_home(request):
    return render(request, 'pages/food-home.html')

@login_required
def grocery_home(request):
    return render(request, 'pages/grocery-home.html')

@login_required
def pharmacy_home(request):
    return render(request, 'pages/pharmacy-home.html')

@login_required
def profile(request):
    return render(request, 'pages/profile.html')

@login_required
def profile_settings(request):
    return render(request, 'pages/profile-settings.html')

@login_required
def manage_delivery_address(request):
    return render(request, 'pages/manage-delivery-address.html')

@login_required
def wishlist(request):
    return render(request, 'pages/wishlist.html')

@login_required
def manage_payment(request):
    return render(request, 'pages/manage-payment.html')

@login_required
def order_history(request):
    return render(request, 'pages/order-history.html')

@login_required
def voucher(request):
    return render(request, 'pages/voucher.html')

@login_required
def app_setting(request):
    return render(request, 'pages/app-setting.html')

@login_required
def notification_setting(request):
    return render(request, 'pages/notification-setting.html')

@login_required
def logout(request):
    return render(request, 'pages/logout.html')

