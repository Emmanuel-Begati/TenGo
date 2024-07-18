# user/urls.py
from django.urls import path
from .views import login_view, signup, logout_view, contact_form

urlpatterns = [
    path('signup/', signup, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('contact/', contact_form, name='contact'),
]
