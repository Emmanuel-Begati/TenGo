from django.shortcuts import render, get_object_or_404, redirect
from restaurant.models import MenuItem
from django.views import View
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import auth
from django.contrib.auth.models import User
from django.contrib import messages




# Create your views here.
def home(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_items = cart.cart_items.all()  # Use related_name here
        print (cart_items)  # Print the cart items to the console
        
        return render(request, 'customer/index.html', {'cart_items': cart_items, 'total_price': cart.total_price()})
    return render(request, 'customer/index.html')

def about(request):
    return render(request, 'customer/about.html')

def contact(request):
    return render(request, 'customer/contact.html')

def base(request):
    return render(request, 'customer/base.html')

def address(request):
    return render(request, 'customer/address.html')

def checkout(request):
    return render(request, 'customer/checkout.html')

def coming_soon(request):
    return render(request, 'customer/coming-soon.html')

def confirm_order(request):
    return render(request, 'customer/confirm-order.html')

def faq(request):
    return render(request, 'customer/faq.html')

def my_order(request):
    return render(request, 'customer/my-order.html')

def offer(request):
    return render(request, 'customer/offer.html')

def order_tracking(request):
    return render(request, 'customer/order-tracking.html')

def otp(request):
    return render(request, 'customer/otp.html' )

def payment(request):
    return render(request, 'customer/payment.html')

def profile(request):
    return render(request, 'customer/profile.html')

def restaurant_listing(request):
    return render(request, 'customer/restaurant-listing.html')

def saved_address(request):
    return render(request, 'customer/saved-address.html')

def saved_card(request):
    return render(request, 'customer/saved-card.html')

def settings(request):
    return render(request, 'customer/settings.html')

def testimonials(request):
    return render(request, 'customer/testimonials.html')

def wishlist(request):
    return render(request, 'customer/wishlist.html')

def menu_grid(request):
    return render(request, 'customer/menu-grid.html')

def menu_listing(request):
    return render(request, 'customer/menu-listing.html')

class Order(View):
    
    def get(self, request, *args, **kwargs):
        appetizers = MenuItem.objects.filter(category__name_contains='Appetizer')
        desserts = MenuItem.objects.filter(category__name_contains='Dessert')
        drinks = MenuItem.objects.filter(category__name_contains='Drink')
        sandwiches = MenuItem.objects.filter(category__name_contains='Sandwich')
        Best_Sellers = MenuItem.objects.filter(category__name_contains='Best Seller')
        Special_Combos = MenuItem.objects.filter(category__name_contains='Special Combos')
        wraps = MenuItem.objects.filter(category__name_contains='Wraps')
        noodles = MenuItem.objects.filter(category__name_contains='Noodles')
        pasta = MenuItem.objects.filter(category__name_contains='Pasta')
        tacos = MenuItem.objects.filter(category__name_contains='Tacos')
        
        
        context = {
            'appetizers': appetizers,
            'desserts': desserts,
            'drinks': drinks,
            'sandwiches': sandwiches,
            'Best_Sellers': Best_Sellers,
            'Special_Combos': Special_Combos,
            'wraps': wraps,
            'noodles': noodles,
            'pasta': pasta,
            'tacos': tacos,
            
        }   
        return render(request, 'customer/order-detail.html', context)   
    
    def post(self, request, *args, **kwargs):
        order_items = {
            'items': []
        }
        items = request.POST.getlist('order')
        for item in items:
            menu_item = MenuItem.objects.get(pk__contains=int(item))
            item_data = {
                'id': menu_item.pk,
                'name': menu_item.name,
                'price': menu_item.price,
            }
            order_items['items'].append(item_data)
            price = 0
            item_ids = []
            for item in order_items['items']:
                price += item['price']
                item_ids.append(item['id'])
            
            order = Order.objects.create(price=price)
            order.items.add(*item_ids)
            context = {
                'items': order_items['items'],
                'price': price,
            }
            return render(request, 'customer/order-detail.html', context)
        
from .models import MenuItem, Cart, CartItem

@login_required
def add_to_cart(request, menu_item):
    menu_item = get_object_or_404(MenuItem, id=menu_item)
    cart, created = Cart.objects.get_or_create(user=request.user)

    cart_item, created = CartItem.objects.get_or_create(cart=cart, menu_item=menu_item)
    if not created:
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart_detail')

@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cart_items.all()  # Use related_name here
    print (cart_items)  # Print the cart items to the console
    return render(request, 'cart_detail.html', {'cart_items': cart_items, 'total_price': cart.total_price()})


@login_required
def remove_from_cart(request):
    if request.method == 'POST':
        cart_item_id = request.POST.get('cart_item_id')
        cart_item = get_object_or_404(CartItem, id=cart_item_id)
        cart_item.delete()
        return JsonResponse({'message': 'Item removed from cart.'})
    return JsonResponse({'error': 'Invalid request.'}, status=400)

@login_required
def empty_cart(request):
    
    return render(request, 'customer/empty-cart.html')
