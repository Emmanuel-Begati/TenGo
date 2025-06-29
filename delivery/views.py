from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, DeliveryPerson
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string

@login_required
def delivery_dashboard(request):
    try:
        delivery_person = DeliveryPerson.objects.get(user=request.user)
    except DeliveryPerson.DoesNotExist:
        delivery_person = None

    pending_deliveries = Order.objects.filter(status='Ready for Delivery')
    accepted_deliveries = Order.objects.filter(
        status__in=['Out for delivery', 'Accepted', 'Delivered'], 
        delivery_person=delivery_person
    )
    
    context = {
        'pending_deliveries': pending_deliveries,
        'accepted_deliveries': accepted_deliveries,
    }
    
    return render(request, 'delivery/delivery.html', context)

def send_notification(channel_layer, group_name, message_data):
    """Helper function to send notifications via WebSocket"""
    async_to_sync(channel_layer.group_send)(group_name, message_data)

@login_required
def accept_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    try:
        delivery_person = DeliveryPerson.objects.get(user=request.user)
    except DeliveryPerson.DoesNotExist:
        error_msg = 'You are not registered as a delivery person.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': error_msg})
        messages.error(request, error_msg)
        return redirect('delivery_dashboard')

    if order.status == 'Ready for Delivery' and delivery_person:
        order.status = 'Accepted'
        order.delivery_person = delivery_person
        order.save()

        channel_layer = get_channel_layer()
        delivery_person_name = f"{delivery_person.user.first_name} {delivery_person.user.last_name}"
        
        # Notification to restaurant
        send_notification(channel_layer, f'restaurant_{order.restaurant.id}', {
            'type': 'order_update',
            'message': f'✅ Order #{order.id} has been accepted by {delivery_person_name}. The delivery person will arrive shortly to collect the order.',
            'order': {
                'id': order.id,
                'status': order.status,
                'delivery_person': delivery_person_name,
                'delivery_person_phone': getattr(delivery_person, 'phone_number', None),
                'delivery_person_email': delivery_person.user.email,
                'acceptance_time': order.order_time.isoformat() if order.order_time else None,
                'estimated_pickup': '10-15 minutes',
            },
        })
        
        # Notification to customer
        send_notification(channel_layer, f'user_{order.user.id}', {
            'type': 'order_update',
            'message': f'🚚 Great news! Your order has been accepted by {delivery_person.user.first_name}. Your food will be delivered soon!',
            'order': {
                'id': order.id,
                'status': order.status,
                'delivery_person': delivery_person_name,
                'delivery_person_phone': getattr(delivery_person, 'phone_number', None),
                'estimated_delivery': '25-35 minutes',
                'tracking_available': True,
                'next_status': 'Your delivery person will pick up the food from the restaurant',
            },
            'notification_type': 'delivery_accepted',
            'priority': 'high'
        })
        
        # Notification to other delivery personnel
        send_notification(channel_layer, "delivery_notifications", {
            "type": "order_update",
            "message": f"Order #{order.id} from {order.restaurant.name} has been accepted by {delivery_person.user.first_name}.",
            "order": {
                "id": order.id,
                "status": order.status,
                "accepted_by": delivery_person_name,
                "restaurant_name": order.restaurant.name,
                "no_longer_available": True,
            },
        })

        success_msg = f'You have successfully accepted order #{order.id}.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'message': success_msg})
        messages.success(request, success_msg)
    else:
        error_msg = 'Unable to accept this order. It may have already been taken.'
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': error_msg})
        messages.error(request, error_msg)

    return redirect('delivery_dashboard')

@login_required
def update_delivery_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        status = request.POST.get('status')
        channel_layer = get_channel_layer()
        delivery_person_name = f"{order.delivery_person.user.first_name} {order.delivery_person.user.last_name}"

        if status == 'Out for delivery' and otp_code == order.restaurant_otp_code:
            order.status = 'Out for delivery'
            order.save()
            messages.success(request, 'Order is now out for delivery!')
            
            # Notifications for "Out for delivery" status
            send_notification(channel_layer, f'restaurant_{order.restaurant.id}', {
                'type': 'order_update',
                'message': f'📦 Order #{order.id} has been successfully picked up by {order.delivery_person.user.first_name} and is now out for delivery.',
                'order': {
                    'id': order.id,
                    'status': order.status,
                    'delivery_person': delivery_person_name,
                    'pickup_confirmed': True,
                    'pickup_time': order.order_time.isoformat() if order.order_time else None,
                },
                'notification_type': 'pickup_confirmed'
            })
            
            send_notification(channel_layer, f'user_{order.user.id}', {
                'type': 'order_update',
                'message': f'🚗 Your order is now out for delivery! {order.delivery_person.user.first_name} is on the way to your location.',
                'order': {
                    'id': order.id,
                    'status': order.status,
                    'delivery_person': delivery_person_name,
                    'delivery_person_phone': getattr(order.delivery_person, 'phone_number', None),
                    'estimated_delivery': '15-25 minutes',
                    'tracking_message': 'Your delivery person has picked up your order and is heading to your location',
                    'can_track': True,
                },
                'notification_type': 'out_for_delivery',
                'priority': 'high'
            })
            
            send_notification(channel_layer, "delivery_notifications", {
                "type": "order_update",
                "message": f"Order #{order.id} is out for delivery by {order.delivery_person.user.first_name}.",
                "order": {
                    "id": order.id,
                    "status": order.status,
                    "delivery_person": delivery_person_name,
                },
            })
            
            return JsonResponse({'success': True})
            
        elif status == 'Delivered' and otp_code == order.customer_otp_code:
            order.status = 'Delivered'
            order.save()
            messages.success(request, 'Order has been successfully delivered!')

            # Notifications for "Delivered" status
            send_notification(channel_layer, f'restaurant_{order.restaurant.id}', {
                'type': 'order_update',
                'message': f'✅ Order #{order.id} has been successfully delivered to {order.user.first_name} {order.user.last_name}.',
                'order': {
                    'id': order.id,
                    'status': order.status,
                    'delivered_at': order.order_time.isoformat() if order.order_time else None,
                    'delivery_person': delivery_person_name,
                    'customer_name': f"{order.user.first_name} {order.user.last_name}",
                    'delivery_confirmed': True,
                },
                'notification_type': 'delivery_completed'
            })
            
            send_notification(channel_layer, f'user_{order.user.id}', {
                'type': 'order_update',
                'message': '🎉 Your order has been delivered! Thank you for choosing TenGo. How was your experience?',
                'order': {
                    'id': order.id,
                    'status': order.status,
                    'delivery_person': delivery_person_name,
                    'delivered_at': order.order_time.isoformat() if order.order_time else None,
                    'action_required': 'rate_order',
                    'rating_prompt': True,
                    'restaurant_name': order.restaurant.name,
                },
                'notification_type': 'delivery_completed',
                'priority': 'high'
            })
            
            send_notification(channel_layer, "delivery_notifications", {
                "type": "order_update",
                "message": f"Order #{order.id} has been delivered successfully by {order.delivery_person.user.first_name}.",
                "order": {
                    "id": order.id,
                    "status": order.status,
                    "delivery_person": delivery_person_name,
                    "completed": True,
                },
            })
            
            return JsonResponse({'success': True})
        else:
            error_msg = 'Invalid OTP code.' if otp_code else 'Invalid status update.'
            messages.error(request, error_msg)
            return JsonResponse({'success': False})

    return redirect('delivery_dashboard')


def get_messages(request):
    return JsonResponse({
        'html': render_to_string('delivery/delivery.html', {'delivery_messages': messages.get_messages(request)})
    })
