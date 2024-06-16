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

def signin(request):
    return render(request, 'customer/signin.html')