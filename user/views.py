from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from .forms import UserRegistrationForm, UserLoginForm, ContactForm
from restaurant.models import Restaurant, Menu
from .models import Contact
from django.contrib import messages



def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            if user.role == 'restaurant':
                user.save()
                restaurant = Restaurant.objects.create(owner=user)
                restaurant.name = user.first_name
                restaurant.description = 'This is a restaurant'
                restaurant.save()
                
                # Create a Menu for the restaurant with the restaurant's name
                menu = Menu.objects.create(name=(f'{restaurant.name} Menu'), 
                                           restaurant=restaurant)
                
                login(request, user)
                return redirect('home')
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
    return render(request, 'customer/contact.html', {'form': form})