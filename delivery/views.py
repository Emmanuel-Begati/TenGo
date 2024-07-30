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
        delivery_person = None

    if order.status == 'Ready for Delivery' and delivery_person:
        order.status = 'Accepted'
        order.delivery_person = delivery_person
        order.save()

        # Notify customer that their order is out for delivery
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'user_{order.user.id}', 
            {
                'type': 'order_update',
                'message': 'Your order is now out for delivery!',
                'order': {
                    'id': order.id,
                    'status': order.status,
                    'delivery_person': delivery_person.user.first_name,
                },
            }
        )

    return redirect('delivery_dashboard')

@login_required
def update_delivery_status(request, order_id):
    order = get_object_or_404(Order, id=order_id)

    if request.method == 'POST':
        otp_code = request.POST.get('otp_code')
        status = request.POST.get('status')

        if status == 'Out for delivery':
            if otp_code == order.restaurant_otp_code:
                order.status = 'Out for delivery'
                order.save()
                
                # Notify customer that their order is out for delivery
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'user_{order.user.id}', 
                    {
                        'type': 'order_update',
                        'message': 'Your order is now out for delivery!',
                        'order': {
                            'id': order.id,
                            'status': order.status,
                        },
                    }
                )
                messages.success(request, 'Order status updated successfully.')
            else:
                messages.error(request, 'Invalid restaurant OTP code.')
        elif status == 'Delivered':
            if otp_code == order.customer_otp_code:
                order.status = 'Delivered'
                order.save()
                
                # Notify customer that their order has been delivered
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'user_{order.user.id}', 
                    {
                        'type': 'order_update',
                        'message': 'Your order has been delivered!',
                        'order': {
                            'id': order.id,
                            'status': order.status,
                        },
                    }
                )
                messages.success(request, 'Order status updated successfully.')
            else:
                messages.error(request, 'Invalid customer OTP code.')
        else:
            messages.error(request, 'Invalid status update.')

    return redirect('delivery_dashboard')
