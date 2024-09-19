# user/urls.py
from django.urls import path
from .views import login_view, signup, logout_view, contact_form, restaurant_form, restaurant_add_address

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('contact/', contact_form, name='contact'),
    path('restaurant-form/', restaurant_form, name='restaurant-form'),
    path('restaurant-add-address/<int:restaurant_id>/',restaurant_add_address, name='restaurant_add_address'),
]
