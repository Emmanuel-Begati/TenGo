from django import forms
from .models import MenuItem, Category, Order, Restaurant, Menu

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['menu','name', 'description', 'price', 'image', 'is_available', 'category']
        widgets = {
            'is_available': forms.CheckboxInput(),
            # 'category': forms.Select(choices=[(category.id, category.name) for category in Category.objects.all()]),
            'menu': forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Extract user from kwargs
        super(MenuItemForm, self).__init__(*args, **kwargs)
        if self.user is not None:
            restaurant = Restaurant.objects.get(owner=self.user)
            self.fields['menu'].queryset = Menu.objects.filter(restaurant=restaurant)

class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']