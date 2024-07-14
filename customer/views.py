from django.shortcuts import render, get_object_or_404, redirect
from restaurant.models import MenuItem
from django.views import View
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import auth
from django.contrib.auth.models import User
from django.contrib import messages
from .models import MenuItem, Cart, CartItem, CardDetails
from django.views.decorators.http import require_POST
import json
from restaurant.models import Category, Order, Restaurant
from django.contrib.auth import get_user_model
from .models import Address
from .forms import AddressForm, CardDetailsForm
from django.db import transaction
from collections import defaultdict
from itertools import groupby




def cart_content(request):
    context = {}
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.cart_items.all()
        total_price = cart.total_price()
        context = {'cart_items': cart_items, 'total_price': total_price}
    return context

@login_required
def home(request):
    if request.user.role == 'restaurant':
        return redirect('restaurant-dashboard')
    else:
        restaurants = Restaurant.objects.all()
        categories = Category.objects.all()  # Fetch all categories
    context = {
        'restaurants': restaurants,
        'categories': categories,  # Add categories to the context
    }
    context.update(cart_content(request))
    return render(request, 'customer/index.html', context=context)

@login_required
def about(request):
    return render(request, 'customer/about.html', context=cart_content(request))

@login_required
def contact(request):
    return render(request, 'customer/contact.html', context=cart_content(request))

@login_required
def base(request):
    return render(request, 'customer/base.html', context=cart_content(request))

@login_required
def address(request):
    addresses = Address.objects.filter(customer=request.user)
    form = AddressForm()  # Instantiate form here
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            # Manually create an Address instance and save form data
            address_instance = Address(
                customer=request.user,
                country=form.cleaned_data['country'],
                state=form.cleaned_data['state'],
                city=form.cleaned_data['city'],
                street=form.cleaned_data['street'],
                zip_code=form.cleaned_data['zip_code'],
                type=form.cleaned_data['type'],
                phone_number=form.cleaned_data['phone_number']
            )
            address_instance.save()
            # Redirect or return a response
            return redirect('address')
    else:
        context = {
            'form': form,
            'addresses': addresses,
            **cart_content(request),  # Merge cart context with the current context
        }
        return render(request, 'customer/address.html', context)
    
    
    
@login_required
def checkout(request):
    cart_context = cart_content(request)  # Get cart context
    context = {
        **cart_context,  # Merge cart context with the current context
    }
    return render(request, 'customer/checkout.html', context=context)

@login_required
def coming_soon(request):
    return render(request, 'customer/coming-soon.html', context=cart_content(request))

@login_required
def confirm_order(request):
    return render(request, 'customer/confirm-order.html', context=cart_content(request))

@login_required
def faq(request):
    return render(request, 'customer/faq.html', context=cart_content(request))

@login_required
def my_order(request):
    orders = Order.objects.filter(user=request.user)
    restaurant = Restaurant.objects.filter(orders__in=orders).distinct().first()
    cart_context = cart_content(request)  # Get cart context
    context = {
        'orders': orders,
        'restaurant': restaurant,
        **cart_context,  # Merge cart context with the current context
    }
    return render(request, 'customer/my-order.html', context=context)

@login_required
def offer(request):
    return render(request, 'customer/offer.html', context=cart_content(request))

@login_required
def order_tracking(request):
    orders = Order.objects.all()
    restaurant = Restaurant.objects.filter(orders__in=orders).distinct().first()
    cart_context = cart_content(request)  # Get cart context
    context = {
        'orders': orders,
        'restaurant': restaurant,
        **cart_context,  # Merge cart context with the current context
    }
    return render(request, 'customer/order-tracking.html', context=context)

@login_required
def otp(request):
    return render(request, 'customer/otp.html', context=cart_content(request))

@login_required
def payment(request):
    if request.method == 'POST':
        # Extract form data
        card_number = request.POST.get('card_number')
        name_on_card = request.POST.get('name_on_card')
        expiry_month = request.POST.get('expiry_month')
        expiry_year = request.POST.get('expiry_year')
        cvv = request.POST.get('cvv')
        zip_code = request.POST.get('zip_code')
        
        # Optionally, validate the form data
        form = CardDetailsForm(request.POST)
        if form.is_valid():
            # Assuming you have a model named CustomerCardDetail and a related customer instance
            customer = request.user  # Example of getting customer instance, adjust based on your user model
            
            # Update or create card details
            card_detail, created = CardDetails.objects.update_or_create(
                customer=customer,
                card_number=card_number,
                expiry_month=expiry_month,
                expiry_year=expiry_year,
                cvv=cvv,
                name_on_card=name_on_card,
                zip_code=zip_code
            )
            cart_items = CartItem.objects.filter(cart__user=request.user)
            cart_items.delete()  # Clear cart items after successful payment
            order = Order.objects.filter(user=request.user).last()
            order.payment_status = True  # Set payment status to success
            # Redirect to a new URL:
            return redirect ('confirm-order')  # Adjust 'success_page' to your actual success page name

    # If this is a GET (or any other method) create the default form.
    else:
        form = CardDetailsForm()
        print (form.errors)
    return render(request, 'customer/payment.html', {'form': form})
    
    context = cart_content(request)
    context['form'] = form  # Add the form to your context
    return render(request, 'customer/payment.html', context)
@login_required
def profile(request):
    return render(request, 'customer/profile.html', context=cart_content(request))

@login_required
def restaurant_listing(request, category_id):
    category =Category.objects.get(id=category_id)
    menu_items = MenuItem.objects.filter(category=category)
    restaurants = Restaurant.objects.filter(menus__menu_items__in=menu_items).distinct()
    context = {
        'restaurants': restaurants,
        'category': category,
        'menu_items': menu_items,
        **cart_content(request),  # Merging cart context with the current context
    }
    print(category)
    print(menu_items)
    print (restaurants)
    return render(request, 'customer/restaurant-listing.html', context=context)

@login_required
def saved_address(request):
    return render(request, 'customer/saved-address.html', context=cart_content(request))

@login_required
def saved_card(request):
    return render(request, 'customer/saved-card.html', context=cart_content(request))

@login_required
def settings(request):
    return render(request, 'customer/settings.html', context=cart_content(request))

@login_required
def testimonials(request):
    return render(request, 'customer/testimonials.html', context=cart_content(request))

@login_required
def wishlist(request):
    return render(request, 'customer/wishlist.html', context=cart_content(request))

@login_required
def menu_grid(request):
    return render(request, 'customer/menu-grid.html', context=cart_content(request))

@login_required
def menu_listing(request, restaurant_id):
    categories_with_items = Category.objects.filter(
        menu_items__isnull=False, menu_items__menu__restaurant_id=restaurant_id
    ).distinct()    
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    menu_items = MenuItem.objects.filter(menu__restaurant=restaurant)
    context = {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'category': categories_with_items,
        **cart_content(request),  # Merging cart context with the current context
    }
    return render(request, 'customer/menu-listing.html', context)

@login_required
def menu_listing1(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    menu_items = MenuItem.objects.filter(menu__restaurant=restaurant)
    categories_with_items = Category.objects.filter(menu_items__isnull=False).distinct()
    cart_context = cart_content(request)  # Get cart context
    context = {
        restaurant: restaurant,
        'menu_items': menu_items,
        'category': categories_with_items,
        **cart_context,  # Merge cart context with the current context
    }
    return render(request, 'customer/menu-listing1.html', context=context)


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cart_items.all()
    return render(request, 'cart_detail.html', {'cart_items': cart_items, 'total_price': cart.total_price()})

import logging
logger = logging.getLogger(__name__)

@login_required
@require_POST
def add_to_cart(request):
    logger.info("Starting add_to_cart view")
    try:
        data = json.loads(request.body)
        menu_item_id = data.get('menu_item_id')
        logger.debug(f"Received menu_item_id: {menu_item_id}")

        if not menu_item_id or not menu_item_id.isdigit():
            logger.warning(f"Invalid menu item ID: {menu_item_id}")
            return JsonResponse({'success': False, 'message': 'Invalid menu item ID'})

        menu_item = get_object_or_404(MenuItem, pk=menu_item_id)
        
        if menu_item.price is None:
            logger.warning(f"Menu item price is None for item ID: {menu_item_id}")
            return JsonResponse({'success': False, 'message': 'Menu item price not set'})

        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)
        cart_item.quantity += 1
        cart_item.price = menu_item.price
        cart_item.save()

        # Calculate new cart count and total price
        new_cart_count = cart.cart_items.count()
        total_price = cart.total_price()

        logger.info(f"Item added to cart: {menu_item_id}")
        return JsonResponse({
            'success': True, 
            'message': 'Item added to cart',
            'new_cart_count': new_cart_count,
            'total_price': str(total_price),  # Convert Decimal to string for JSON serialization
            'menu_item': {
                'image': menu_item.image.url if menu_item.image else '',  # Assuming MenuItem has an image field
                'name': menu_item.name,
            },
            'quantity': cart_item.quantity,
            'price': str(cart_item.price),  # Convert Decimal to string for JSON serialization
            'cart_item_id': cart_item.id,
            
        })
    except Exception as e:
        logger.error(f"Error in add_to_cart: {str(e)}")
        return JsonResponse({'success': False, 'message': 'An error occurred'})

@login_required
@require_POST
def remove_from_cart(request):
    cart_item_id = request.POST.get('cart_item_id')
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    return JsonResponse({'message': 'Item removed from cart.'})

@login_required
@require_POST
def empty_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.cart_items.all().delete()
    return render(request, 'customer/empty-cart.html')

@login_required
def use_address(request, address_id):
    orders = Order.objects.filter(user=request.user)
    customer_address = get_object_or_404(Address, id=address_id, customer=request.user)
    for order in orders:
        order.delivery_address = customer_address.street + ', ' + customer_address.city
        order.save()
        print (order.delivery_address)
    return redirect('payment')  
    
        
@login_required
def create_order(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)
    
    if not cart_items:
        messages.error(request, "Your cart is empty. Please add items before creating an order.")
        return redirect('menu_listing')  # Redirect to menu or appropriate page
    
    orders_created = []
    
    with transaction.atomic():
        for restaurant, items in groupby(cart_items, key=lambda x: x.menu_item.menu.restaurant):
            items = list(items)  # Convert to list as groupby returns an iterator
            total_price = sum(item.total_price() for item in items)
            
            order = Order.objects.create(
                user=request.user,
                restaurant=restaurant,
                total=total_price,
                status='Pending'
            )
            
            for cart_item in items:
                order.items.add(cart_item.menu_item)
            
            orders_created.append(order)
        
   
    messages.success(request, f"Successfully created {len(orders_created)} order(s).")
    return redirect('address')  # Redirect to address selection page

