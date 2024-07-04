from django.shortcuts import render, redirect
from .models import Order, Restaurant
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from restaurant.models import MenuItem, Menu
import json
from .forms import MenuItemForm



# Create your views here.
def resturant_dashboard(request):
    if request.user.role != 'restaurant':
        return redirect('home')
    elif request.user.role == 'restaurant':
        return render(request, 'restaurant/restaurant-dashboard.html')
    else:
        return redirect('home')
    

@login_required
def order_list(request):
    # Assuming the user is the owner of the restaurant
    user = request.user
    # Retrieve Restaurant instances owned by the user
    restaurants = Restaurant.objects.filter(owner=user)
    # Filter orders by the retrieved restaurants
    orders = Order.objects.filter(restaurant__in=restaurants)
    # Render your template with the orders context
    return render(request, 'restaurant/order-list.html', {'orders': orders})

@login_required
def add_menu_item(request):
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('menu-item-list')  # Redirect to a new URL
    else:
        form = MenuItemForm()
    return render(request, 'restaurant/add-menu-item.html', {'form': form})


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