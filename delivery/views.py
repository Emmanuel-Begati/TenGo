from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Order, DeliveryPerson
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib import messages

@login_required
def delivery_dashboard(request):
    try:
        delivery_person = DeliveryPerson.objects.get(user=request.user)
    except DeliveryPerson.DoesNotExist:
        delivery_person = None

    pending_deliveries = Order.objects.filter(status='Ready for Delivery')
    accepted_deliveries = Order.objects.filter(status__in=['Out for delivery'], delivery_person=delivery_person)
    
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
        messages.error(request, "You are not authorized to accept deliveries.")
        return redirect('delivery_dashboard')

    order.status = 'Out for delivery'
    order.delivery_person = delivery_person
    order.save()

    # Send notification to WebSocket group
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            'delivery_notifications', 
            {
                'type': 'send_notification', 
                'message': f'Order {order.id} has been accepted by {delivery_person.user.first_name}.',
                'order': {
                    'id': order.id,
                    'restaurant_name': order.restaurant.name,
                    'customer_name': order.user.first_name,
                    'customer_address': order.delivery_address,
                    'status': order.status
                },
                'csrf_token': request.META.get("CSRF_COOKIE")
            }
        )

    return redirect('delivery_dashboard')

@login_required
def update_delivery_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    
    new_status = request.POST.get('status')
    if new_status not in ['Out for delivery', 'Delivered']:
        messages.error(request, "Invalid status update.")
        return redirect('delivery_dashboard')

    order.status = new_status
    order.save()

    # Send notification to WebSocket group
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            'delivery_notifications', 
            {
                'type': 'send_notification', 
                'message': f'Order {order.id} status updated to {new_status}.',
                'order': {
                    'id': order.id,
                    'restaurant_name': order.restaurant.name,
                    'customer_name': order.user.first_name,
                    'customer_address': order.delivery_address,
                    'status': order.status
                },
                'csrf_token': request.META.get("CSRF_COOKIE")
            }
        )

    return redirect('delivery_dashboard')
