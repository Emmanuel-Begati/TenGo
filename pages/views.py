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

@login_required
def details(request):
    return render(request, 'pages/details.html')

@login_required
def cart(request):
    return render(request, 'pages/cart.html')

@login_required
def coupon(request):
    return render(request, 'pages/coupon.html')

@login_required
def address(request):
    return render(request, 'pages/address.html')

@login_required
def confirm_location(request):
    return render(request, 'pages/confirm-location.html')

@login_required
def payment_method(request):
    return render(request, 'pages/payment-method.html')

@login_required
def new_card(request):
    return render(request, 'pages/new-card.html')

@login_required
def order_tracking(request):
    return render(request, 'pages/order-tracking.html')

@login_required
def order_details(request):
    return render(request, 'pages/order-details.html')

@login_required
def chatting(request):
    return render(request, 'pages/chatting.html')

@login_required
def page_listing(request):
    return render(request, 'pages/page-listing.html')

@login_required
def onboarding(request):
    return render(request, 'pages/onboarding.html')

@login_required
def otp(request):
    return render(request, 'pages/otp.html')

@login_required
def listing(request):
    return render(request, 'pages/listing.html')

@login_required
def brand_list(request):
    return render(request, 'pages/brand-list.html')

@login_required
def categories(request):
    return render(request, 'pages/categories.html')

@login_required
def address_details(request):
    return render(request, 'pages/address-details.html')

@login_required
def offer(request):
    return render(request, 'pages/offer.html')

@login_required
def notification(request):
    return render(request, 'pages/notification.html')

@login_required
def other_setting(request):
    return render(request, 'pages/other-setting.html')

@login_required
def empty_cart(request):
    return render(request, 'pages/empty-cart.html')

@login_required
def empty_wishlist(request):
    return render(request, 'pages/empty-wishlist.html')

@login_required
def empty_notification(request):
    return render(request, 'pages/empty-notification.html')

@login_required
def empty_search(request):
    return render(request, 'pages/empty-search.html')

@login_required
def search(request):
    return render(request, 'pages/search.html')