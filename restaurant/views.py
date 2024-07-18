from django.shortcuts import render, redirect, get_object_or_404
from .models import Order, Restaurant, RestaurantAnalysis
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from restaurant.models import MenuItem, Menu, Order
import json
from .forms import MenuItemForm, OrderStatusUpdateForm
from datetime import datetime, timedelta




# Create your views here.
def resturant_dashboard(request):
    if request.user.role != 'restaurant':
        return redirect('home')
    elif request.user.role == 'restaurant':
        recent_threshold = datetime.now() - timedelta(days=7)
        recent_orders = Order.objects.filter(order_time__gte=recent_threshold)
        restaurant = Restaurant.objects.get(owner=request.user)
        restaurant_analysis, created = RestaurantAnalysis.objects.get_or_create(restaurant=restaurant)
        return render(request, 'restaurant/restaurant-dashboard.html', {'recent_orders': recent_orders, 'restaurant_analysis': restaurant_analysis})
    else:
        return redirect('home')
    

@login_required
def order_list(request):
    user = request.user
    restaurants = Restaurant.objects.filter(owner=user ).values_list('id', flat=True)
    orders = Order.objects.filter(restaurant__in=restaurants, is_visible_to_restaurant=True)

    # Calculate and save the total for each order
    for order in orders:
        order_total = order.calculate_total()
        order.total = order_total  
        order.save()

    return render(request, 'restaurant/order-list.html', {'orders': orders})

@login_required
def add_menu_item(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            menu_item = form.save(commit=False)
            # Assuming you have a way to determine the menu to assign
            menu_item.menu = Menu.objects.get(restaurant__owner=request.user)
            menu_item.save()
            return redirect('menu-item-list')  # Redirect to a new URL
    else:
        form = MenuItemForm()
        print (form.errors)

    return render(request, 'restaurant/add-menu-item.html', {'form': form})

@login_required
def edit_menu_item(request, menu_item_id):
    menu_item = get_object_or_404(MenuItem, menu_item_id=menu_item_id)
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=menu_item, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('menu-item-list')  # Redirect to the menu item list page or wherever appropriate
    else:
        form = MenuItemForm(instance=menu_item, user=request.user)
    return render(request, 'restaurant/edit-menu-item.html', {'form': form})


def menu_item_list(request):
    user = request.user
    if user.role == 'restaurant':
        # Assuming each user is linked to one restaurant
        restaurant = Restaurant.objects.get(owner=user)
        # Assuming a Restaurant has a direct relation to Menu(s)
        menus = Menu.objects.filter(restaurant=restaurant)
        menu_items = MenuItem.objects.filter(menu__in=menus)
        return render(request, 'restaurant/menu-item-list.html', {'menu_items': menu_items})

    else:
        return redirect('home')
    
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == 'POST':
        form = OrderStatusUpdateForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('order-list')  # Adjust the redirect to your order list page's name
    else:
        form = OrderStatusUpdateForm(instance=order)
    return render(request, 'restaurant/update_order_status.html', {'form': form, 'order': order})


def delete_menu_item(request, menu_item_id):
    menu_item = get_object_or_404(MenuItem, menu_item_id=menu_item_id)
    print (menu_item)
    menu_item.delete()
    return redirect('menu-item-list')  # Adjust the redirect as needed