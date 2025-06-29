from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.cache import cache_page
from datetime import datetime, timedelta
import json

from .models import Order, Restaurant, RestaurantAnalysis, MenuItem, Menu
from .forms import MenuItemForm, OrderStatusUpdateForm
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


# Create your views here.
@login_required
def restaurant_dashboard(request):
    if request.user.role != "restaurant":
        return redirect("home")
    
    recent_threshold = datetime.now() - timedelta(days=7)
    # Optimize query with select_related
    recent_orders = Order.objects.filter(
        order_time__gte=recent_threshold
    ).select_related('user', 'restaurant').order_by('-order_time')
    
    restaurant = get_object_or_404(Restaurant, owner=request.user)
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


@login_required
def order_list(request):
    user = request.user
    restaurant = get_object_or_404(Restaurant, owner=user)
    
    # Optimized query with select_related and prefetch_related
    orders = Order.objects.filter(
        restaurant=restaurant, 
        is_visible_to_restaurant=True
    ).select_related(
        'user', 'restaurant', 'delivery_person'
    ).prefetch_related(
        'items__category'
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
            # Optimized query to get menu
            menu_item.menu = get_object_or_404(Menu, restaurant__owner=request.user)
            menu_item.restaurant = menu_item.menu.restaurant  # Set restaurant directly
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


@login_required
def menu_item_list(request):
    if request.user.role != "restaurant":
        return redirect("home")
    
    # Optimized query with select_related
    restaurant = get_object_or_404(Restaurant, owner=request.user)
    menu_items = MenuItem.objects.filter(
        restaurant=restaurant
    ).select_related(
        'restaurant', 'menu'
    ).prefetch_related(
        'category'
    )
    return render(
        request,
        "restaurant/menu-item-list.html",
        {"menu_items": menu_items, "restaurant": restaurant},
    )


def delete_menu_item(request, menu_item_id):
    menu_item = get_object_or_404(MenuItem, menu_item_id=menu_item_id)
    print(menu_item)
    menu_item.delete()
    return redirect(
        "menu-item-list",
    )  # Adjust the redirect as needed


@login_required
def update_order_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    if request.method == "POST":
        form = OrderStatusUpdateForm(request.POST, instance=order)
        if form.is_valid():
            old_status = order.status
            order = form.save()
            channel_layer = get_channel_layer()
            
            if order.status == "Ready for Delivery":
                # Enhanced notification to all delivery personnel with comprehensive order details
                async_to_sync(channel_layer.group_send)(
                    "delivery_notifications",
                    {
                        "type": "send_notification",
                        "message": f"🍕 New delivery opportunity! Order #{order.id} from {order.restaurant.name} is ready for pickup.",
                    },
                )

                # Send the complete order data for the delivery dashboard with enhanced details
                async_to_sync(channel_layer.group_send)(
                    "order_updates",
                    {
                        "type": "send_order_data",
                        "order": {
                            "id": order.id,
                            "restaurant_name": order.restaurant.name,
                            "restaurant_id": order.restaurant.id,
                            "restaurant_address": (
                                f"{order.restaurant.address.street}, {order.restaurant.address.city}, {order.restaurant.address.country}"
                                if order.restaurant.address else "Restaurant Address"
                            ),
                            "customer_name": f"{order.user.first_name} {order.user.last_name}".strip(),
                            "customer_phone": order.user.phone if hasattr(order.user, 'phone') else None,
                            "customer_address": order.delivery_address,
                            "status": order.status,
                            "total": str(order.total),
                            "order_time": order.order_time.isoformat() if order.order_time else None,
                            "restaurant_otp": order.restaurant_otp_code,
                            "items_count": order.items.count(),
                            "special_instructions": order.special_instructions if hasattr(order, 'special_instructions') else None,
                            "priority": "normal",
                            "estimated_prep_time": "5-10 minutes",
                        },
                    },
                )

                # Enhanced notification to customer about readiness for delivery
                async_to_sync(channel_layer.group_send)(
                    f"user_{order.user.id}",
                    {
                        "type": "order_update",
                        "message": f"🍳 Great news! Your order from {order.restaurant.name} is ready and will be picked up by a delivery person soon.",
                        "order": {
                            "id": order.id,
                            "status": order.status,
                            "restaurant": order.restaurant.name,
                            "estimated_pickup_time": "5-10 minutes",
                            "next_step": "A delivery person will accept your order and pick it up",
                            "tracking_enabled": True,
                        },
                        "notification_type": "ready_for_delivery",
                        "priority": "medium"
                    },
                )
                
            elif order.status in ["Preparing", "Confirmed"]:
                # Enhanced notifications to customer about order preparation status
                status_messages = {
                    "Confirmed": "🎉 Your order has been confirmed! The restaurant is starting to prepare your delicious food.",
                    "Preparing": "👨‍🍳 Your order is being prepared with care by our kitchen team. It won't be long now!"
                }
                
                async_to_sync(channel_layer.group_send)(
                    f"user_{order.user.id}",
                    {
                        "type": "order_update",
                        "message": status_messages.get(order.status, f"Your order status has been updated to {order.status}."),
                        "order": {
                            "id": order.id,
                            "status": order.status,
                            "restaurant": order.restaurant.name,
                            "estimated_prep_time": "15-20 minutes" if order.status == "Preparing" else "20-25 minutes",
                            "next_step": "Ready for delivery" if order.status == "Preparing" else "Preparing",
                        },
                        "notification_type": "preparation_update",
                        "priority": "medium"
                    },
                )
                
            elif order.status == "Cancelled":
                # Enhanced notifications for order cancellation with refund information
                async_to_sync(channel_layer.group_send)(
                    f"user_{order.user.id}",
                    {
                        "type": "order_update",
                        "message": f"😔 We're sorry, but your order from {order.restaurant.name} has been cancelled. You will receive a full refund within 3-5 business days.",
                        "order": {
                            "id": order.id,
                            "status": order.status,
                            "restaurant": order.restaurant.name,
                            "refund_amount": str(order.total),
                            "refund_timeline": "3-5 business days",
                            "action_required": "refund_initiated",
                            "support_available": True,
                        },
                        "notification_type": "order_cancelled",
                        "priority": "high"
                    },
                )
                
                # If there was a delivery person assigned, notify them with enhanced details
                if order.delivery_person:
                    async_to_sync(channel_layer.group_send)(
                        "delivery_notifications",
                        {
                            "type": "order_update",
                            "message": f"❌ Order #{order.id} from {order.restaurant.name} has been cancelled by the restaurant. This order is no longer available.",
                            "order": {
                                "id": order.id,
                                "status": order.status,
                                "restaurant_name": order.restaurant.name,
                                "cancelled_by": "restaurant",
                                "reason": "Restaurant cancelled",
                                "remove_from_dashboard": True,
                            },
                        },
                    )

            return redirect("order-list")
    else:
        form = OrderStatusUpdateForm(instance=order)
    return render(request, "restaurant/update_order_status.html", {"form": form})
