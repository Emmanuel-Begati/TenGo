from django.urls import path
import restaurant.views as views


urlpatterns = [
    path('restaurant-dashboard', views.resturant_dashboard, name='restaurant-dashboard'),
    path('order-list', views.order_list, name='order-list'),
    ]