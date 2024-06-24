
from django.urls import path
import customer.views as views


urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
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
    path('saved-card/', views.saved_card, name='saved-card'),
    path('settings/', views.settings, name='settings'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('menu-grid/', views.menu_grid, name='menu-grid'),
    path('menu-listing/', views.menu_listing, name='menu-listing'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
]
