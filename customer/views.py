import json
import logging
import environ
from collections import defaultdict
from itertools import groupby

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.db import transaction
from django.contrib.auth import get_user_model

from restaurant.models import MenuItem, Category, Order, Restaurant
from .models import Cart, CartItem, CardDetails, Address
from .forms import AddressForm, CardDetailsForm
from .flutterwave_utils import initialize_payment, verify_payment
from user.forms import UpdateForm
from rave_python import Rave, RaveExceptions, Misc
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


def cart_content(request):
    """Optimized cart content with caching"""
    context = {}
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
        # Use select_related to reduce database queries
        cart_items = cart.cart_items.select_related('menu_item').all()
        total_price = cart.total_price()
        context = {"cart_items": cart_items, "total_price": total_price}
    return context


@login_required
def home(request):
    if request.user.role == "restaurant":
        return redirect("restaurant-dashboard")
    elif request.user.role == "delivery_person":
        return redirect("delivery_dashboard")
    else:
        # Optimized queries
        restaurants = Restaurant.objects.select_related('address')
        
        # Sort in Python to avoid database ordering (faster for small datasets)
        restaurants_list = list(restaurants)
        restaurants_by_rating = sorted(restaurants_list, key=lambda x: x.rating, reverse=True)
        restaurants_by_delivery_time = sorted(restaurants_list, key=lambda x: x.delivery_time)
        restaurants_by_cost = sorted(restaurants, key=lambda x: x.average_cost)
        categories = Category.objects.all()  # Fetch all categories
    context = {
        "restaurants": restaurants,
        "restaurants_by_rating": restaurants_by_rating,
        "restaurants_by_delivery_time": restaurants_by_delivery_time,
        "restaurants_by_cost": restaurants_by_cost,
        "categories": categories,  # Add categories to the context
    }
    context.update(cart_content(request))
    return render(request, "customer/index.html", context=context)


@login_required
def about(request):
    return render(request, "customer/about.html", context=cart_content(request))


@login_required
def contact(request):
    return render(request, "customer/contact.html", context=cart_content(request))


@login_required
def base(request):
    return render(request, "customer/base.html", context=cart_content(request))


@login_required
def address(request):
    addresses = Address.objects.filter(customer=request.user)
    form = AddressForm()  # Instantiate form here
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            # Manually create an Address instance and save form data
            address_instance = Address(
                customer=request.user,
                country=form.cleaned_data["country"],
                state=form.cleaned_data["state"],
                city=form.cleaned_data["city"],
                street=form.cleaned_data["street"],
                zip_code=form.cleaned_data["zip_code"],
                type=form.cleaned_data["type"],
                phone_number=form.cleaned_data["phone_number"],
            )
            address_instance.save()
            # Redirect or return a response
            return redirect("address")
    else:
        context = {
            "form": form,
            "addresses": addresses,
            **cart_content(request),  # Merge cart context with the current context
        }
        return render(request, "customer/address.html", context)


@login_required
def checkout(request):
    cart_context = cart_content(request)  # Get cart context
    context = {
        **cart_context,  # Merge cart context with the current context
    }
    return render(request, "customer/checkout.html", context=context)


@login_required
def coming_soon(request):
    return render(request, "customer/coming-soon.html", context=cart_content(request))


@login_required
def confirm_order(request):
    # Directly fetch unpaid orders for this user
    unpaid_orders = Order.objects.filter(user=request.user, payment_status=False)

    if not unpaid_orders.exists():
        messages.error(
            request,
            "No pending orders found to confirm. Your orders may already be confirmed or you haven't placed any.",
        )
        return redirect("my-order")

    orders_updated = 0
    update_failed = []

    # Process each order individually to avoid transaction issues
    for order in unpaid_orders:
        try:
            # Update each order's statuses directly
            order.payment_status = True
            order.is_visible_to_restaurant = True
            order.save()

            # Enhanced WebSocket notification to restaurant with comprehensive order details
            try:
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"restaurant_{order.restaurant.id}",
                    {
                        "type": "order_update",
                        "message": f"💰 New paid order received! Order #{order.id} has been confirmed and paid by {order.user.first_name} {order.user.last_name}.",
                        "order": {
                            "id": order.id,
                            "status": order.status,
                            "payment_status": order.payment_status,
                            "customer_name": f"{order.user.first_name} {order.user.last_name}",
                            "customer_phone": order.user.phone if hasattr(order.user, 'phone') else None,
                            "total_amount": str(order.total),
                            "delivery_address": order.delivery_address,
                            "order_time": order.order_time.isoformat() if order.order_time else None,
                            "items_count": order.items.count(),
                            "payment_method": "Card",
                            "priority": "new_order",
                        },
                        "notification_type": "new_paid_order",
                        "priority": "high"
                    },
                )
                
                # Also notify the customer about successful payment
                async_to_sync(channel_layer.group_send)(
                    f"user_{order.user.id}",
                    {
                        "type": "payment_update",
                        "message": f"✅ Payment successful! Your order #{order.id} from {order.restaurant.name} has been confirmed and sent to the restaurant.",
                        "order": {
                            "id": order.id,
                            "status": order.status,
                            "payment_status": True,
                            "restaurant": order.restaurant.name,
                            "total_amount": str(order.total),
                            "estimated_prep_time": "20-30 minutes",
                            "next_step": "Restaurant is preparing your order",
                        },
                        "notification_type": "payment_confirmed",
                        "priority": "high"
                    },
                )
            except Exception as e:
                print(f"Error notifying restaurant for order {order.id}: {str(e)}")

            orders_updated += 1
        except Exception as e:
            update_failed.append(order.id)
            print(f"Failed to update order {order.id}: {str(e)}")

    # Clear the cart after confirmation attempts
    CartItem.objects.filter(cart__user=request.user).delete()

    if orders_updated > 0:
        messages.success(
            request,
            f"Your {orders_updated} order(s) have been confirmed, payment completed, and your cart has been cleared.",
        )
    else:
        messages.error(
            request,
            "Failed to confirm any orders. Please try again or contact customer service.",
        )

    if update_failed:
        messages.warning(
            request,
            f"Some orders ({', '.join(map(str, update_failed))}) could not be updated. Please check their status.",
        )

    # After confirmation, fetch the updated orders to verify changes
    confirmed_orders = Order.objects.filter(
        user=request.user,
        id__in=[order.id for order in unpaid_orders],
        payment_status=True,
        is_visible_to_restaurant=True,
    )

    context = cart_content(request)
    context["confirmed_orders"] = confirmed_orders
    return render(request, "customer/confirm-order.html", context=context)


@login_required
def faq(request):
    return render(request, "customer/faq.html", context=cart_content(request))


@login_required
def my_order(request):
    # Get orders for the current user and sort by order_time in descending order (newest first)
    orders = Order.objects.filter(user=request.user).order_by("-order_time")
    restaurant = Restaurant.objects.filter(orders__in=orders).distinct().first()
    cart_context = cart_content(request)  # Get cart context
    context = {
        "orders": orders,
        "restaurant": restaurant,
        **cart_context,  # Merge cart context with the current context
    }
    return render(request, "customer/my-order.html", context=context)


@login_required
def offer(request):
    return render(request, "customer/offer.html", context=cart_content(request))


@login_required
def order_tracking(request):
    # Sort orders by newest first
    orders = Order.objects.filter(user=request.user).order_by("-order_time")
    restaurant = Restaurant.objects.filter(orders__in=orders).distinct().first()
    cart_context = cart_content(request)  # Get cart context
    context = {
        "orders": orders,
        "restaurant": restaurant,
        **cart_context,  # Merge cart context with the current context
    }
    return render(request, "customer/order-tracking.html", context=context)


@login_required
def otp(request):
    return render(request, "customer/otp.html", context=cart_content(request))


@login_required
def profile(request):
    user = request.user
    form = UpdateForm(instance=user)  # Pass the user instance to pre-populate the form
    if request.method == "POST":
        form = UpdateForm(request.POST, instance=user)
        if form.is_valid():
            # Check if data was changed before updating
            for field, value in form.cleaned_data.items():
                if getattr(user, field, None) != value:
                    setattr(user, field, value)
            user.save()
        else:
            print(form.errors)
        return redirect("profile")
    else:
        user_details = {
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "phone_number": user.phone_number,
        }

        context = {
            "user": user_details,
            **cart_content(request),  # Merging cart context with the current context
        }
        return render(request, "customer/profile.html", context=context)


@login_required
def restaurant_listing(request, category_id):
    category = Category.objects.get(id=category_id)
    menu_items = MenuItem.objects.filter(category=category)
    restaurants = Restaurant.objects.filter(menus__menu_items__in=menu_items).distinct()
    context = {
        "restaurants": restaurants,
        "category": category,
        "menu_items": menu_items,
        **cart_content(request),  # Merging cart context with the current context
    }
    return render(request, "customer/restaurant-listing.html", context=context)


@login_required
def saved_address(request):
    addresses = Address.objects.filter(customer=request.user)
    form = AddressForm()  # Instantiate form here
    if request.method == "POST":
        form = AddressForm(request.POST)
        if form.is_valid():
            # Manually create an Address instance and save form data
            address_instance = Address(
                customer=request.user,
                country=form.cleaned_data["country"],
                state=form.cleaned_data["state"],
                city=form.cleaned_data["city"],
                street=form.cleaned_data["street"],
                zip_code=form.cleaned_data["zip_code"],
                type=form.cleaned_data["type"],
                phone_number=form.cleaned_data["phone_number"],
            )
            address_instance.save()
            # Redirect or return a response
            return redirect("saved-address")
    else:
        customer_addresses = Address.objects.filter(customer=request.user)
        context = {
            "customer_addresses": customer_addresses,
            **cart_content(request),  # Merging cart context with the current context
        }
        return render(request, "customer/saved-address.html", context=context)


@login_required
def saved_card(request):
    return render(request, "customer/saved-card.html", context=cart_content(request))


@login_required
def settings(request):
    return render(request, "customer/settings.html", context=cart_content(request))


@login_required
def testimonials(request):
    return render(request, "customer/testimonials.html", context=cart_content(request))


@login_required
def wishlist(request):
    return render(request, "customer/wishlist.html", context=cart_content(request))


@login_required
def menu_grid(request):
    return render(request, "customer/menu-grid.html", context=cart_content(request))


@login_required
def menu_listing(request, restaurant_id):
    categories_with_items = Category.objects.filter(
        menu_items__isnull=False, menu_items__menu__restaurant_id=restaurant_id
    ).distinct()
    restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
    menu_items = MenuItem.objects.filter(menu__restaurant=restaurant)
    primary_categories = Category.objects.filter(
        primary_menu_items__menu__restaurant=restaurant
    ).distinct()

    context = {
        "restaurant": restaurant,
        "menu_items": menu_items,
        "category": categories_with_items,
        "primary_categories": primary_categories,
        **cart_content(request),  # Merging cart context with the current context
    }
    return render(request, "customer/menu-listing.html", context)


@login_required
def cart_detail(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.cart_items.all()
    return render(
        request,
        "cart_detail.html",
        {"cart_items": cart_items, "total_price": cart.total_price()},
    )


# ============ AJAX VIEWS ============


@login_required
@require_POST
def add_to_cart(request):
    logger.info("Starting add_to_cart view")
    try:
        # Parse the incoming request data
        data = json.loads(request.body)
        menu_item_id = data.get("menu_item_id")
        logger.debug(f"Received menu_item_id: {menu_item_id}")

        # Validate menu_item_id
        if not menu_item_id or not menu_item_id.isdigit():
            logger.warning(f"Invalid menu item ID: {menu_item_id}")
            return JsonResponse({"success": False, "message": "Invalid menu item ID"})

        # Fetch the menu item from the database
        menu_item = get_object_or_404(MenuItem, pk=menu_item_id)

        # Check if the menu item has a price set
        if menu_item.price is None:
            logger.warning(f"Menu item price is None for item ID: {menu_item_id}")
            return JsonResponse(
                {"success": False, "message": "Menu item price not set"}
            )

        # Get or create the cart for the user
        cart, created = Cart.objects.get_or_create(user=request.user)

        # Get or create the cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, menu_item=menu_item
        )
        cart_item.quantity += 1  # Increment quantity
        cart_item.price = menu_item.price  # Set the item price
        cart_item.save()

        # Calculate new cart count and total price
        new_cart_count = cart.cart_items.count()
        total_price = sum(
            item.menu_item.price * item.quantity
            for item in CartItem.objects.filter(cart=cart)
        )

        # Log the successful addition to cart
        logger.info(f"Item added to cart: {menu_item_id}")

        # Return the updated cart details as JSON response
        return JsonResponse(
            {
                "success": True,
                "message": "Item added to cart",
                "new_cart_count": new_cart_count,
                "total_price": str(
                    total_price
                ),  # Convert Decimal to string for JSON serialization
                "menu_item": {
                    "image": menu_item.image.url
                    if menu_item.image
                    else "",  # Assuming MenuItem has an image field
                    "name": menu_item.name,
                },
                "quantity": cart_item.quantity,
                "price": str(
                    cart_item.price
                ),  # Convert Decimal to string for JSON serialization
                "cart_item_id": cart_item.id,
            }
        )

    except Exception as e:
        # Log any error that occurred
        logger.error(f"Error in add_to_cart: {str(e)}")
        return JsonResponse({"success": False, "message": "An error occurred"})


@login_required
@require_POST
def remove_from_cart(request):
    cart_item_id = request.POST.get("cart_item_id")
    cart_item = get_object_or_404(CartItem, id=cart_item_id)
    cart_item.delete()
    return JsonResponse({"message": "Item removed from cart."})


@login_required
@require_POST
def empty_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.cart_items.all().delete()
    return render(request, "customer/empty-cart.html")


@login_required
@require_POST
def update_cart_quantity(request):
    try:
        # Parse the incoming JSON data
        data = json.loads(request.body)
        cart_item_id = data.get("cart_item_id")
        action = data.get("action")

        # Validate input
        if not cart_item_id or action not in ["increase", "decrease"]:
            return JsonResponse(
                {"success": False, "message": "Invalid input parameters"}
            )

        # Get the cart item
        cart_item = get_object_or_404(CartItem, id=cart_item_id)

        # Update quantity based on action
        if action == "increase":
            cart_item.quantity += 1
            cart_item.save()
        elif action == "decrease":
            if cart_item.quantity <= 1:
                # Remove item if quantity would become 0
                cart_item.delete()
                cart = Cart.objects.get(user=request.user)
                return JsonResponse(
                    {
                        "success": True,
                        "removed": True,
                        "message": "Item removed from cart",
                        "cart_count": cart.cart_items.count(),
                        "total_price": str(cart.total_price()),
                    }
                )
            else:
                cart_item.quantity -= 1
                cart_item.save()

        # Get updated cart information
        cart = Cart.objects.get(user=request.user)
        total_price = cart.total_price()

        # Calculate item total (price * quantity)
        item_total = cart_item.price * cart_item.quantity

        return JsonResponse(
            {
                "success": True,
                "removed": False,
                "quantity": cart_item.quantity,
                "item_total": str(item_total),
                "total_price": str(total_price),
                "cart_count": cart.cart_items.count(),
            }
        )

    except Exception as e:
        return JsonResponse({"success": False, "message": str(e)})


@login_required
def use_address(request, address_id):
    orders = Order.objects.filter(user=request.user)
    customer_address = get_object_or_404(Address, id=address_id, customer=request.user)
    for order in orders:
        order.delivery_address = (
            customer_address.street
            + ", "
            + customer_address.city
            + ", "
            + customer_address.state
            + ", "
            + customer_address.country
        )
        order.save()
    return redirect("make_payment")


# -------------------------------------------------------------ORDER SECTION--------------------------------------------------------------
@login_required
def create_order(request):
    cart = get_object_or_404(Cart, user=request.user)
    cart_items = CartItem.objects.filter(cart=cart)

    if not cart_items:
        messages.error(
            request, "Your cart is empty. Please add items before creating an order."
        )
        return redirect("empty-cart")  # Redirect to menu or appropriate page

    orders_created = []

    try:
        with transaction.atomic():
            for restaurant, items in groupby(
                cart_items, key=lambda x: x.menu_item.menu.restaurant
            ):
                items = list(items)  # Convert to list as groupby returns an iterator
                total_price = sum(item.total_price() for item in items)

                order = Order.objects.create(
                    user=request.user,
                    restaurant=restaurant,
                    total=total_price,
                    status="Pending",
                    is_visible_to_restaurant=False,  # Set visibility to False
                )

                for cart_item in items:
                    order.items.add(cart_item.menu_item)

                orders_created.append(order)

        channel_layer = get_channel_layer()
        for order in orders_created:
            # Notify restaurant about new order with enhanced details
            async_to_sync(channel_layer.group_send)(
                f"restaurant_{order.restaurant.id}",
                {
                    "type": "new_order",
                    "message": f"📋 New order #{order.id} received from {order.user.first_name} {order.user.last_name}. Ready to be processed.",
                    "order": {
                        "id": order.id,
                        "status": order.status,
                        "customer_name": f"{order.user.first_name} {order.user.last_name}",
                        "customer_phone": order.user.phone if hasattr(order.user, 'phone') else None,
                        "total": str(order.total),
                        "items_count": order.items.count(),
                        "order_time": order.order_time.isoformat() if order.order_time else None,
                        "restaurant_id": order.restaurant.id,
                        "payment_status": order.payment_status,
                    },
                },
            )

        messages.success(
            request, f"Successfully created {len(orders_created)} order(s)."
        )
    except Exception as e:
        messages.error(request, f"An error occurred while creating the order: {e}")
        return redirect("home")

    return redirect("address")  # Redirect to address selection page


# -------------------------------------------------------------SEARCH SECTION--------------------------------------------------------------
def restaurant_search(request):
    query = request.GET.get("q")
    if query:
        results = Restaurant.objects.filter(name__icontains=query)
        results_for_food_items = MenuItem.objects.filter(name__icontains=query)

        # Create a list of dictionaries containing restaurant and corresponding menu item details
        results_for_food = []
        for item in results_for_food_items:
            results_for_food.append(
                {"restaurant": item.menu.restaurant, "menu_item": item}
            )

        restaurants = results.order_by("delivery_time")
    else:
        restaurants = Restaurant.objects.none()
        results_for_food = []

    context = {
        "restaurants": restaurants,
        "query": query,
        **cart_content(request),  # Merging cart context with the current context
        "results_for_food": results_for_food,
    }

    return render(request, "customer/restaurant_search_results.html", context)


# ---------------------------------------------------------------------------pAYMENT SECTION--------------------------------------------------------------

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()

# Initialize Rave
rave = Rave(
    env("FLUTTERWAVE_PUBLIC_KEY"), env("FLUTTERWAVE_SECRET_KEY"), usingEnv=False
)


def make_payment(request):
    card_detail = None
    # Get all orders for the user that have not been paid for yet
    orders = Order.objects.filter(user=request.user, payment_status=False)

    if not orders.exists():
        messages.error(request, "No unpaid orders found.")
        return redirect("cart")  # Redirect to cart or appropriate page

    card_details = CardDetails.objects.filter(customer=request.user)

    if request.method == "POST":
        selected_card_id = request.POST.get("selected_card")
        if selected_card_id:
            card_detail = CardDetails.objects.get(
                id=selected_card_id, customer=request.user
            )
            return process_payment_with_saved_card(request, card_detail, orders)
        else:
            form = CardDetailsForm(request.POST)
            if form.is_valid():
                return process_payment_with_new_card(request, form, orders)
    else:
        form = CardDetailsForm()

    context = {
        "form": form,
        "card_details": card_details,
        "orders": orders,  # Passing all unpaid orders to the template
    }
    context.update(cart_content(request))  # Assuming you need cart context too
    return render(request, "customer/payment.html", context)


def process_payment_with_saved_card(request, card_detail, orders):
    for order in orders:
        payload = {
            "cardno": card_detail.card_number,
            "cvv": card_detail.cvv,
            "expirymonth": card_detail.expiry_month,
            "expiryyear": card_detail.expiry_year,
            "email": request.user.email,
            "amount": str(order.total),  # Process each order separately
            "currency": "USD",
            "suggested_auth": "PIN",
        }

        # Charge the card for each order
        response = charge_card(request, payload)
        if response.status_code != 200:  # Handle errors
            return response  # If one payment fails, stop and return the error

    return redirect("confirm-order")  # Redirect when all orders are processed


def process_payment_with_new_card(request, form, orders):
    cardno = form.cleaned_data["card_number"]
    cvv = form.cleaned_data["cvv"]
    expirymonth = form.cleaned_data["expiry_month"]
    expiryyear = form.cleaned_data["expiry_year"]
    zip_code = form.cleaned_data["zip_code"]

    card_detail, created = CardDetails.objects.update_or_create(
        customer=request.user,
        card_number=cardno,
        expiry_month=expirymonth,
        expiry_year=expiryyear,
        cvv=cvv,
        defaults={
            "name_on_card": request.user.first_name + " " + request.user.last_name,
            "zip_code": zip_code,
        },
    )

    for order in orders:
        payload = {
            "cardno": cardno,
            "cvv": cvv,
            "expirymonth": expirymonth,
            "expiryyear": expiryyear,
            "email": request.user.email,
            "amount": str(order.total),  # Process each order separately
            "currency": "USD",
            "suggested_auth": "PIN",
        }

        # Charge the card for each order
        response = charge_card(request, payload)
        if response.status_code != 200:  # Handle errors
            return response  # If one payment fails, stop and return the error

    return redirect("confirm-order")  # Redirect when all orders are processed


def charge_card(request, payload):
    try:
        res = rave.Card.charge(payload)

        if res["suggestedAuth"]:
            arg = Misc.getTypeOfArgsRequired(res["suggestedAuth"])
            Misc.updatePayload(
                res["suggestedAuth"], payload, pin="3310", otp="12345"
            )  # Securely collect these details
            res = rave.Card.charge(payload)

        if res["validationRequired"]:
            rave.Card.validate(res["flwRef"], "12345")  # Securely collect OTP

        verification = rave.Card.verify(res["txRef"])
        if verification["transactionComplete"]:
            handle_successful_payment(request)
            return JsonResponse({"status": "success"})
        else:
            return JsonResponse({"status": "failed", "details": verification})

    except RaveExceptions.CardChargeError as e:
        return JsonResponse({"status": "error", "message": str(e)})
    except RaveExceptions.TransactionValidationError as e:
        return JsonResponse({"status": "error", "message": str(e)})
    except RaveExceptions.TransactionVerificationError as e:
        return JsonResponse({"status": "error", "message": str(e)})


def handle_successful_payment(request):
    try:
        # Find all unpaid orders for this user
        unpaid_orders = Order.objects.filter(user=request.user, payment_status=False)

        if not unpaid_orders.exists():
            messages.error(request, "No unpaid orders found to process.")
            return False

        # Mark all unpaid orders as paid and visible to restaurant
        with transaction.atomic():
            updated_count = unpaid_orders.update(
                payment_status=True, is_visible_to_restaurant=True
            )

            # Verify the update was successful
            if updated_count == 0:
                messages.error(request, "Failed to update your order payment status.")
                return False

            # Clear the cart after payment
            CartItem.objects.filter(cart__user=request.user).delete()

            # Enhanced WebSocket notifications to restaurants with detailed order information
            try:
                channel_layer = get_channel_layer()
                for order in Order.objects.filter(
                    id__in=unpaid_orders.values_list("id", flat=True)
                ):
                    # Notify restaurant with comprehensive order details
                    async_to_sync(channel_layer.group_send)(
                        f"restaurant_{order.restaurant.id}",
                        {
                            "type": "order_update",
                            "message": f"🎉 New order confirmed! Order #{order.id} has been paid and is ready for preparation.",
                            "order": {
                                "id": order.id,
                                "status": order.status,
                                "payment_status": order.payment_status,
                                "customer_name": f"{order.user.first_name} {order.user.last_name}",
                                "customer_phone": order.user.phone if hasattr(order.user, 'phone') else None,
                                "total_amount": str(order.total),
                                "delivery_address": order.delivery_address,
                                "order_time": order.order_time.isoformat() if order.order_time else None,
                                "items_count": order.items.count(),
                                "payment_confirmed": True,
                                "needs_preparation": True,
                            },
                            "notification_type": "new_paid_order",
                            "priority": "high"
                        },
                    )
                    
                    # Notify customer about successful payment and order progression
                    async_to_sync(channel_layer.group_send)(
                        f"user_{order.user.id}",
                        {
                            "type": "payment_update", 
                            "message": f"✅ Payment successful! Your order from {order.restaurant.name} has been confirmed and sent to the restaurant for preparation.",
                            "order": {
                                "id": order.id,
                                "status": order.status,
                                "payment_status": True,
                                "restaurant": order.restaurant.name,
                                "total_amount": str(order.total),
                                "next_step": "Restaurant will start preparing your order",
                                "estimated_total_time": "35-45 minutes",
                            },
                            "notification_type": "payment_success",
                            "priority": "high"
                        },
                    )
            except Exception as e:
                # Log WebSocket notification errors but don't fail the payment
                print(f"Error notifying restaurants and customers: {str(e)}")

            messages.success(
                request, f"{updated_count} order(s) have been successfully paid for."
            )
            return True

    except Exception as e:
        messages.error(request, f"Error processing payment: {str(e)}")
        return False
