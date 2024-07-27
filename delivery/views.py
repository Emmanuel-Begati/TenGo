from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .models import DeliveryPerson, Order

@login_required
def delivery_dashboard(request):
    try:
        delivery_person = DeliveryPerson.objects.get(user=request.user)
    except DeliveryPerson.DoesNotExist:
        delivery_person = None

    pending_deliveries = Order.objects.filter(status='Pending')
    accepted_deliveries = Order.objects.filter(status='Accepted', delivery_person=delivery_person)
    context = {
        'pending_deliveries': pending_deliveries,
        'accepted_deliveries': accepted_deliveries,
    }
    return render(request, 'delivery/delivery.html', context)

@login_required
def accept_delivery(request, order_id):
    order = Order.objects.get(id=order_id)
    try:
        delivery_person = DeliveryPerson.objects.get(user=request.user)
    except DeliveryPerson.DoesNotExist:
        return redirect('delivery_dashboard')  # or handle the error appropriately

    order.status = 'Accepted'
    order.delivery_person = delivery_person
    order.save()

    # Send notification to WebSocket group
    channel_layer = get_channel_layer()
    if channel_layer:
        async_to_sync(channel_layer.group_send)(
            'delivery_notifications', 
            {'type': 'send_notification', 'message': 'A new order has been accepted.'}
        )
    else:
        # Handle the case where the channel layer is not available
        print("Channel layer is not available")

    return redirect('delivery_dashboard')


@login_required
def update_delivery_status(request, order_id):
    order = Order.objects.get(id=order_id)
    new_status = request.POST.get('status')
    order.status = new_status
    order.save()
    return redirect('delivery_dashboard')