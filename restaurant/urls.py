from django.urls import path
import restaurant.views as views


urlpatterns = [
    path('restaurant-dashboard', views.resturant_dashboard, name='restaurant-dashboard'),
    path('order-list', views.order_list, name='order-list'),
    path('add-menu-item', views.add_menu_item, name='add-menu-item'),
    path('menu-item-list/', views.menu_item_list, name='menu-item-list'),
    path('order/<int:order_id>/update_status/', views.update_order_status, name='update_order_status'),


    ]