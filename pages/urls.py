from django.urls import path, include
from . import views
from django.contrib.auth.views import LogoutView


urlpatterns = [
 path('home/', views.home, name='home'),
 path('', views.home, name='home'),
path('location/', views.location, name='location'),
path('landing/', views.landing, name='landing'),
path('food-home/', views.food_home, name='food-home'),
path('grocery-home/', views.grocery_home, name='grocery-home'),
path('pharmacy-home/', views.pharmacy_home, name='pharmacy-home'),
path('profile', views.profile, name='profile'),
path('profile-settings', views.profile_settings, name='profile-settings'),
path('manage-delivery-address', views.manage_delivery_address, name='manage-delivery-address'),
path('wishlist', views.wishlist, name='wishlist'),
path('manage-payment', views.manage_payment, name='manage-payment'),
path('order-history', views.order_history, name='order-history'),
path('voucher', views.voucher, name='voucher'),
path('app-setting', views.app_setting, name='app-setting'),
path('notification-setting', views.notification_setting, name='notification-setting'),
path('logout/', LogoutView.as_view(), name='logout'),

]

