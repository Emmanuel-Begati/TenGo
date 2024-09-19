from django import forms
from .models import MenuItem, Category, Order, Restaurant, Menu

class MenuItemForm(forms.ModelForm):
    category = forms.ModelMultipleChoiceField(
        queryset=Category.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'is_available', 'category', 'preparation_time', 'image']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Extract user from kwargs
        super(MenuItemForm, self).__init__(*args, **kwargs)
        if self.user is not None:
            # Ensure that the queryset for the 'restaurant' field is set to Restaurant instances
            self.fields['restaurant'].queryset = Restaurant.objects.filter(owner=self.user)

class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = ['name', 'description', 'phone', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Restaurant Name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Brief Description'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Phone'}),
            'image': forms.FileInput(attrs={'class': 'form-control'}),
        }