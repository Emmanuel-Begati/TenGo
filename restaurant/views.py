from django.shortcuts import render, redirect
from .models import Order, Restaurant
from django.contrib.auth.decorators import login_required

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
