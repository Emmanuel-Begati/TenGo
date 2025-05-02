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
def restaurant_dashboard(request):
    if request.user.role != "restaurant":
        return redirect("home")
    elif request.user.role == "restaurant":
        recent_threshold = datetime.now() - timedelta(days=7)
        recent_orders = Order.objects.filter(order_time__gte=recent_threshold)
        restaurant = Restaurant.objects.get(owner=request.user)
        restaurant_analysis, created = RestaurantAnalysis.objects.get_or_create(
            restaurant=restaurant
        )
        return render(
            request,
            "restaurant/restaurant-dashboard.html",
            {
                "recent_orders": recent_orders,
                "restaurant_analysis": restaurant_analysis,
                "restaurant": restaurant,
            },
        )
    else:
        return redirect("home")


@login_required
def order_list(request):
    user = request.user
    restaurants = Restaurant.objects.filter(owner=user).values_list("id", flat=True)
    restaurant = Restaurant.objects.get(owner=request.user)
    # Update to order by order_time in descending order (newest first)
    orders = Order.objects.filter(
        restaurant__in=restaurants, is_visible_to_restaurant=True
    ).order_by("-order_time")

    return render(
        request,
        "restaurant/order-list.html",
        {"orders": orders, "restaurant": restaurant},
    )


@login_required
def add_menu_item(request):
    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.menu = Menu.objects.get(restaurant__owner=request.user)
            menu_item.save()
            form.save_m2m()  # Save the many-to-many data for the form
            return redirect("menu-item-list")
    else:
        form = MenuItemForm()
    return render(request, "restaurant/add-menu-item.html", {"form": form})


@login_required
def edit_menu_item(request, menu_item_id):
    menu_item = get_object_or_404(MenuItem, menu_item_id=menu_item_id)
    if request.method == "POST":
        form = MenuItemForm(request.POST, request.FILES, instance=menu_item)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.save()
            form.save_m2m()  # Save the many-to-many data for the form
            return redirect("menu-item-list")
    else:
        form = MenuItemForm(instance=menu_item)
    return render(request, "restaurant/edit-menu-item.html", {"form": form})


def menu_item_list(request):
    user = request.user
    if user.role == "restaurant":
        # Assuming each user is linked to one restaurant
        restaurant = Restaurant.objects.get(owner=user)
        # Assuming a Restaurant has a direct relation to Menu(s)
        menus = Menu.objects.filter(restaurant=restaurant)
        menu_items = MenuItem.objects.filter(menu__in=menus)
        return render(
            request,
            "restaurant/menu-item-list.html",
            {"menu_items": menu_items, "restaurant": restaurant},
        )

    else:
        return redirect("home")


def delete_menu_item(request, menu_item_id):
    menu_item = get_object_or_404(MenuItem, menu_item_id=menu_item_id)
    print(menu_item)
    menu_item.delete()
    return redirect(
        "menu-item-list",
    )  # Adjust the redirect as needed


# restaurant/views.py
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        form = OrderStatusUpdateForm(request.POST, instance=order)
        if form.is_valid():
            order = form.save()
            if order.status == "Ready for Delivery":
                channel_layer = get_channel_layer()

                # First, notify all delivery personnel that a new order is ready
                async_to_sync(channel_layer.group_send)(
                    "delivery_notifications",
                    {
                        "type": "send_notification",
                        "message": f"Order #{order.id} from {order.restaurant.name} is ready for delivery.",
                    },
                )

                # Then, send the complete order data for the delivery dashboard
                async_to_sync(channel_layer.group_send)(
                    "order_updates",
                    {
                        "type": "send_order_data",
                        "order": {
                            "id": order.id,
                            "restaurant_name": order.restaurant.name,
                            "restaurant_id": order.restaurant.id,
                            "customer_name": f"{order.user.first_name} {order.user.last_name}".strip(),
                            "customer_address": order.delivery_address,
                            "status": order.status,
                            "total": str(order.total),
                            "order_time": order.order_time.isoformat()
                            if order.order_time
                            else None,
                        },
                    },
                )

                # Also notify the customer that their order is ready for delivery
                try:
                    async_to_sync(channel_layer.group_send)(
                        f"user_{order.user.id}",
                        {
                            "type": "order_update",
                            "message": "Your order is ready for delivery!",
                            "order": {
                                "id": order.id,
                                "status": order.status,
                            },
                        },
                    )
                except Exception as e:
                    print(f"Error notifying customer: {str(e)}")

            return redirect("order-list")
    else:
        form = OrderStatusUpdateForm(instance=order)
    return render(request, "restaurant/update_order_status.html", {"form": form})
