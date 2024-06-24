from django.shortcuts import render, get_object_or_404, redirect
from restaurant.models import MenuItem
from django.views import View
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import auth
from django.contrib.auth.models import User
from django.contrib import messages
from .models import MenuItem, Cart, CartItem


def cart_content(request):
    context = {}
    if request.user.is_authenticated:
        cart = Cart.objects.get(user=request.user)
        cart_items = cart.cart_items.all()
        total_price = cart.total_price()
        context = {'cart_items': cart_items, 'total_price': total_price}
    return context

@login_required
def home(request):
    return render(request, 'customer/index.html', context=cart_content(request))

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
    return render(request, 'customer/address.html', context=cart_content(request))

@login_required
def checkout(request):
    return render(request, 'customer/checkout.html', context=cart_content(request))

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
    return render(request, 'customer/my-order.html', context=cart_content(request))

@login_required
def offer(request):
    return render(request, 'customer/offer.html', context=cart_content(request))

@login_required
def order_tracking(request):
    return render(request, 'customer/order-tracking.html', context=cart_content(request))

@login_required
def otp(request):
    return render(request, 'customer/otp.html', context=cart_content(request))

@login_required
def payment(request):
    return render(request, 'customer/payment.html', context=cart_content(request))

@login_required
def profile(request):
    return render(request, 'customer/profile.html', context=cart_content(request))

@login_required
def restaurant_listing(request):
    return render(request, 'customer/restaurant-listing.html', context=cart_content(request))

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
def menu_listing(request):
    return render(request, 'customer/menu-listing.html', context=cart_content(request))

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
