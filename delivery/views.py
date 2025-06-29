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
    accepted_deliveries = Order.objects.filter(status__in=['Out for delivery', 'Accepted', 'Delivered'], delivery_person=delivery_person)
    
    context = {
        'pending_deliveries': pending_deliveries,
        'accepted_deliveries': accepted_deliveries,
    }
    
    return render(request, 'delivery/delivery.html', context)

@login_required
def accept_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    try:
        delivery_person = DeliveryPerson.objects.get(user=request.user)
    except DeliveryPerson.DoesNotExist:
        messages.error(request, 'You are not registered as a delivery person.')
        return redirect('delivery_dashboard')

    if order.status == 'Ready for Delivery' and delivery_person:
        order.status = 'Accepted'
        order.delivery_person = delivery_person
        order.save()

        # Get channel layer for WebSocket communication
        channel_layer = get_channel_layer()
        
        # Enhanced notification to restaurant with more details
        async_to_sync(channel_layer.group_send)(
            f'restaurant_{order.restaurant.id}', 
            {
                'type': 'order_update',
                'message': f'✅ Order #{order.id} has been accepted by {delivery_person.user.first_name} {delivery_person.user.last_name}. The delivery person will arrive shortly to collect the order.',
                'order': {
                    'id': order.id,
                    'status': order.status,
                    'delivery_person': f"{delivery_person.user.first_name} {delivery_person.user.last_name}",
                    'delivery_person_phone': delivery_person.phone_number if hasattr(delivery_person, 'phone_number') else None,
                    'delivery_person_email': delivery_person.user.email,
                    'acceptance_time': order.order_time.isoformat() if order.order_time else None,
                    'estimated_pickup': '10-15 minutes',
                },
            }
        )
        
        # Enhanced notification to customer with detailed information
        async_to_sync(channel_layer.group_send)(
            f'user_{order.user.id}', 
            {
                'type': 'order_update',
                'message': f'🚚 Great news! Your order has been accepted by {delivery_person.user.first_name}. Your food will be delivered soon!',
                'order': {
                    'id': order.id,
                    'status': order.status,
                    'delivery_person': f"{delivery_person.user.first_name} {delivery_person.user.last_name}",
                    'delivery_person_phone': delivery_person.phone_number if hasattr(delivery_person, 'phone_number') else None,
                    'estimated_delivery': '25-35 minutes',
                    'tracking_available': True,
                    'next_status': 'Your delivery person will pick up the food from the restaurant',
                },
                'notification_type': 'delivery_accepted',
                'priority': 'high'
            }
        )
        
        # Notify other delivery personnel that this order is no longer available
        async_to_sync(channel_layer.group_send)(
            "delivery_notifications",
            {
                "type": "order_update",
                "message": f"Order #{order.id} from {order.restaurant.name} has been accepted by {delivery_person.user.first_name}.",
                "order": {
                    "id": order.id,
                    "status": order.status,
                    "accepted_by": f"{delivery_person.user.first_name} {delivery_person.user.last_name}",
                    "restaurant_name": order.restaurant.name,
                    "no_longer_available": True,
                },
            },
        )

        messages.success(request, f'You have successfully accepted order #{order.id}.')
    else:
        messages.error(request, 'Unable to accept this order. It may have already been taken.')

    # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        if order.status == 'Accepted':
            return JsonResponse({'success': True, 'message': f'Successfully accepted order #{order.id}'})
        else:
            return JsonResponse({'success': False, 'message': 'Unable to accept this order. It may have already been taken.'})

    return redirect('delivery_dashboard')

@login_required
def update_delivery_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        status = request.POST.get('status')
        channel_layer = get_channel_layer()

        if status == 'Out for delivery':
            if otp_code == order.restaurant_otp_code:
                order.status = 'Out for delivery'
                order.save()
                messages.success(request, 'Order is now out for delivery!')
                
                # Enhanced notification to restaurant with pickup confirmation
                async_to_sync(channel_layer.group_send)(
                    f'restaurant_{order.restaurant.id}', 
                    {
                        'type': 'order_update',
                        'message': f'📦 Order #{order.id} has been successfully picked up by {order.delivery_person.user.first_name} and is now out for delivery.',
                        'order': {
                            'id': order.id,
                            'status': order.status,
                            'delivery_person': f"{order.delivery_person.user.first_name} {order.delivery_person.user.last_name}",
                            'pickup_confirmed': True,
                            'pickup_time': order.order_time.isoformat() if order.order_time else None,
                        },
                        'notification_type': 'pickup_confirmed'
                    }
                )
                
                # Enhanced notification to customer with detailed tracking info
                async_to_sync(channel_layer.group_send)(
                    f'user_{order.user.id}', 
                    {
                        'type': 'order_update',
                        'message': f'🚗 Your order is now out for delivery! {order.delivery_person.user.first_name} is on the way to your location.',
                        'order': {
                            'id': order.id,
                            'status': order.status,
                            'delivery_person': f"{order.delivery_person.user.first_name} {order.delivery_person.user.last_name}",
                            'delivery_person_phone': order.delivery_person.phone_number if hasattr(order.delivery_person, 'phone_number') else None,
                            'estimated_delivery': '15-25 minutes',
                            'tracking_message': 'Your delivery person has picked up your order and is heading to your location',
                            'can_track': True,
                        },
                        'notification_type': 'out_for_delivery',
                        'priority': 'high'
                    }
                )
                
                # Update all delivery personnel about the status change
                async_to_sync(channel_layer.group_send)(
                    "delivery_notifications",
                    {
                        "type": "order_update",
                        "message": f"Order #{order.id} is out for delivery by {order.delivery_person.user.first_name}.",
                        "order": {
                            "id": order.id,
                            "status": order.status,
                            "delivery_person": f"{order.delivery_person.user.first_name} {order.delivery_person.user.last_name}",
                        },
                    },
                )
                
                return JsonResponse({'success': True})
            else:
                messages.error(request, 'Invalid restaurant OTP code.')
                return JsonResponse({'success': False})
            
        elif status == 'Delivered':
            if otp_code == order.customer_otp_code:
                order.status = 'Delivered'
                order.save()
                messages.success(request, 'Order has been successfully delivered!')

                # Enhanced notification to restaurant with delivery confirmation
                async_to_sync(channel_layer.group_send)(
                    f'restaurant_{order.restaurant.id}', 
                    {
                        'type': 'order_update',
                        'message': f'✅ Order #{order.id} has been successfully delivered to {order.user.first_name} {order.user.last_name}.',
                        'order': {
                            'id': order.id,
                            'status': order.status,
                            'delivered_at': order.order_time.isoformat() if order.order_time else None,
                            'delivery_person': f"{order.delivery_person.user.first_name} {order.delivery_person.user.last_name}",
                            'customer_name': f"{order.user.first_name} {order.user.last_name}",
                            'delivery_confirmed': True,
                        },
                        'notification_type': 'delivery_completed'
                    }
                )
                
                # Enhanced notification to customer with delivery confirmation and rating prompt
                async_to_sync(channel_layer.group_send)(
                    f'user_{order.user.id}', 
                    {
                        'type': 'order_update',
                        'message': '🎉 Your order has been delivered! Thank you for choosing TenGo. How was your experience?',
                        'order': {
                            'id': order.id,
                            'status': order.status,
                            'delivery_person': f"{order.delivery_person.user.first_name} {order.delivery_person.user.last_name}",
                            'delivered_at': order.order_time.isoformat() if order.order_time else None,
                            'action_required': 'rate_order',
                            'rating_prompt': True,
                            'restaurant_name': order.restaurant.name,
                        },
                        'notification_type': 'delivery_completed',
                        'priority': 'high'
                    }
                )
                
                # Update all delivery personnel about successful delivery
                async_to_sync(channel_layer.group_send)(
                    "delivery_notifications",
                    {
                        "type": "order_update",
                        "message": f"Order #{order.id} has been delivered successfully by {order.delivery_person.user.first_name}.",
                        "order": {
                            "id": order.id,
                            "status": order.status,
                            "delivery_person": f"{order.delivery_person.user.first_name} {order.delivery_person.user.last_name}",
                            "completed": True,
                        },
                    },
                )
                
                return JsonResponse({'success': True})
            else:
                messages.error(request, 'Invalid customer OTP code.')
                return JsonResponse({'success': False})
        else:
            messages.error(request, 'Invalid status update.')
            return JsonResponse({'success': False})

    return redirect('delivery_dashboard')


def get_messages(request):
    return JsonResponse({
        'html': render_to_string('delivery/delivery.html', {'messages': messages.get_messages(request)})
    })
