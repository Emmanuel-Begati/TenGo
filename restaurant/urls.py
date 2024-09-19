from django.urls import path
import restaurant.views as views


urlpatterns = [
    path('restaurant-dashboard', views.restaurant_dashboard, name='restaurant-dashboard'),
    path('order-list', views.order_list, name='order-list'),
    path('add-menu-item', views.add_menu_item, name='add-menu-item'),
    path('edit-menu-item/<int:menu_item_id>/', views.edit_menu_item, name='edit-menu-item'),
    path('menu-item-list/', views.menu_item_list, name='menu-item-list'),
    path('order/<int:order_id>/update_status/', views.update_order_status, name='update_order_status'),
    path('delete-menu-item/<int:menu_item_id>/', views.delete_menu_item, name='delete-menu-item'),

    

    ]