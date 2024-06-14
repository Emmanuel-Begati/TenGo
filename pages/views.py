from django.shortcuts import render
from django.contrib.auth.decorators import login_required

# Create your views here.
def home(request):
    return render(request, 'pages/index.html')

@login_required
def location(request):
    return render(request, 'pages/location.html')

@login_required
def landing(request):
    return render(request, 'pages/landing.html')