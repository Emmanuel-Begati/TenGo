
from django.urls import path
import customer.views as views


urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('contact/', views.contact, name='contact'),
    path('address/', views.address, name='address'),
    path('checkout/', views.checkout, name='checkout'),
    path('coming-soon/', views.coming_soon, name='coming-soon'),
    path('confirm-order/', views.confirm_order, name='confirm-order'),
    path('faq/', views.faq, name='faq'),
    path('my-order/', views.my_order, name='my-order'),
    path('offer/', views.offer, name='offer'),
    path('order-tracking/', views.order_tracking, name='order-tracking'),
    path('otp/', views.otp, name='otp'),
    path('payment/', views.payment, name='payment'),
    path('profile/', views.profile, name='profile'),
    path('restaurant-listing/', views.restaurant_listing, name='restaurant-listing'),
    path('saved-address/', views.saved_address, name='saved-address'),
]
