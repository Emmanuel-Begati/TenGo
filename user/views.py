from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import UserRegistrationForm, UserLoginForm, CustomAuthenticationForm

def signup(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'user/signup.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, request.POST)
        if form.is_valid():
            login(request, form.get_user())
            # Redirect to a success page after login
            return redirect('home')  # Replace with your success URL name
        else:
            print(form.errors)  
    else:
        form = CustomAuthenticationForm(request)

    return render(request, 'user/login.html', {'form': form})