from django.shortcuts import render

# Create your views here.
def home(request):
    return render(request, 'customer/index.html')

def about(request):
    return render(request, 'customer/about.html')

def contact(request):
    return render(request, 'customer/contact.html')

def base(request):
    return render(request, 'customer/base.html')

def login(request):
    return render(request, 'customer/login.html')

def signup(request):
    return render(request, 'customer/signup.html')

def address(request):
    return render(request, 'customer/address.html')

def checkout(request):
    return render(request, 'customer/checkout.html')

def coming_soon(request):
    return render(request, 'customer/coming-soon.html')

def confirm_order(request):
    return render(request, 'customer/confirm-order.html')