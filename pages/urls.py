from django.urls import path, include
from . import views


urlpatterns = [
 path('home/', views.home, name='home'),
 path('', views.home, name='home'),
path('location/', views.location, name='location'),
path('landing/', views.landing, name='landing'),


]

