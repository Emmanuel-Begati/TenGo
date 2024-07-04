from django import forms
from .models import MenuItem, Category, Order

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['menu', 'name', 'description', 'price', 'image', 'is_available', 'category']
        widgets = {
            'is_available': forms.CheckboxInput(),
            'category': forms.Select(choices=[(category.id, category.name) for category in Category.objects.all()]),
            # Assuming you want to use a select widget for the menu as well
            'menu': forms.Select(),
        }
        

class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']