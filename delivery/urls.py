from django.urls import path
from . import views

urlpatterns = [
    path('delivery/', views.delivery_dashboard, name='delivery_dashboard'),
    path('delivery/accept/<int:order_id>/', views.accept_delivery, name='accept_delivery'),
    path('delivery/update/<int:order_id>/', views.update_delivery_status, name='update_delivery_status'),

]
