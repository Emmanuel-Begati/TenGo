from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, UserLoginForm, ContactForm ,RestaurantAddressForm
from restaurant.models import Restaurant, Menu, RestaurantAddress
from .models import Contact
from django.contrib import messages
from restaurant.forms import RestaurantForm
from django.contrib.auth.decorators import login_required


def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == 'restaurant':
                user.save()
                login(request, user)
                return redirect('restaurant-form')
            else:
                login(request, user)
                messages.success(request, 'Signup successful! Welcome to the platform.')
                return redirect('home')  # Redirect to home if the user role is not 'restaurant'
        else:
            print(form.errors)
    else:
        form = UserRegistrationForm()
    return render(request, 'user/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            if request.user.role == 'restaurant':
                return redirect('restaurant-dashboard')
            else:
                return redirect('home')  # Replace 'home' with your desired redirect URL
        else:
            print(form.errors)
    else:
        form = UserLoginForm(request)
    return render(request, 'user/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def contact_form(request):
    if request.method == 'POST':
        form = ContactForm(data=request.POST)
        if form.is_valid():
            contact_instance = Contact(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                phone_number=form.cleaned_data['phone_number'],
                message=form.cleaned_data['message']
            )
            contact_instance.save()
            # Add a success message
            messages.success(request, 'Your message has been sent successfully')
            return redirect('home')
        else:
            print(form.errors)
    else:
        form = ContactForm()
    return render(request, 'user/contact.html', {'form': form})


def restaurant_form(request):
    if request.user.role == 'restaurant':
        if request.method == 'POST':
            form = RestaurantForm(request.POST, request.FILES)
            if form.is_valid():
                restaurant = form.save(commit=False)
                restaurant.owner = request.user
                restaurant.save()
                # Create a Menu for the restaurant with the restaurant's name
                menu = Menu.objects.create(name=f'{restaurant.name} Menu', restaurant=restaurant)
                return redirect('restaurant_add_address', restaurant_id=restaurant.id)  # Redirect to the new address form
            else:
                print(form.errors)
        else:
            form = RestaurantForm()
    else:
        return redirect('home')
    return render(request, 'restaurant/restaurant-form.html', {'form': form})

@login_required
def restaurant_add_address(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    if request.method == 'POST':
        form = RestaurantAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.restaurant_related = restaurant  # Set the restaurant_related field
            address.save()
            restaurant.address = address  # Set the address field in the Restaurant model
            restaurant.save()
            return redirect('restaurant-dashboard')  # Redirect to the restaurant dashboard after saving the address
    else:
        form = RestaurantAddressForm()
    return render(request, 'restaurant/restaurant_add_address.html', {'form': form, 'restaurant': restaurant})