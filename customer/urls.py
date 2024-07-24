
from django.urls import path
import customer.views as views


urlpatterns = [
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('address/', views.address, name='address'),
    path('coming-soon/', views.coming_soon, name='coming-soon'),
    path('confirm-order/', views.confirm_order, name='confirm-order'),
    path('faq/', views.faq, name='faq'),
    path('my-order/', views.my_order, name='my-order'),
    path('offer/', views.offer, name='offer'),
    path('order-tracking/', views.order_tracking, name='order-tracking'),
    path('otp/', views.otp, name='otp'),
    # path('payment/', views.payment, name='payment'),
    # path('payment/callback/', views.payment_callback, name='payment_callback'),
    path('profile/', views.profile, name='profile'),
    path('restaurant-listing/<int:category_id>/', views.restaurant_listing, name='restaurant-listing'),
    path('saved-address/', views.saved_address, name='saved-address'),
    path('saved-card/', views.saved_card, name='saved-card'),
    path('settings/', views.settings, name='settings'),
    path('testimonials/', views.testimonials, name='testimonials'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('menu-grid/', views.menu_grid, name='menu-grid'),
    path('menu-listing/<int:restaurant_id>/', views.menu_listing, name='menu-listing'),
    path('menu-listing/', views.menu_listing, name='menu-listing'),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('remove_from_cart/', views.remove_from_cart, name='remove_from_cart'),
    path('empty-cart/', views.empty_cart, name='empty_cart'),
    path('menu-listing1/', views.menu_listing1, name='menu-listing1'),
    path('checkout/', views.checkout, name='checkout'),
    path('use_address/<int:address_id>/', views.use_address, name='use_address'),
    path('create_order/', views.create_order, name='create_order'),
    path('search/', views.restaurant_search, name='restaurant_search'),
    path('make_payment/', views.make_payment, name='make_payment'),

]
