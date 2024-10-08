# user/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from .models import User, Contact
from django.utils.translation import gettext, gettext_lazy as _
from restaurant.models import RestaurantAddress
from .validators import CustomPasswordValidator
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError  # Add this import




class UserRegistrationForm(UserCreationForm):
    role = forms.ChoiceField(choices=User.ROLE_CHOICES, required=True)
    
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'role', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(UserRegistrationForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter your first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter your last name'
        self.fields['password1'].widget.attrs['placeholder'] = 'Enter your password'
        self.fields['password2'].widget.attrs['placeholder'] = 'Confirm your password'

class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(widget=forms.EmailInput(attrs={'autofocus': True}))
    
    
    
class UpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone_number']
        
    def __init__(self, *args, **kwargs):
        super(UpdateForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email'
        self.fields['first_name'].widget.attrs['placeholder'] = 'Enter your first name'
        self.fields['last_name'].widget.attrs['placeholder'] = 'Enter your last name'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter your phone number'
        self.fields['first_name'].widget.attrs['readonly'] = True
        self.fields['first_name'].widget.attrs['disabled'] = True
        self.fields['first_name'].widget.attrs['style'] = 'background-color: #e9ecef;'
        self.fields['last_name'].widget.attrs['readonly'] = True
        self.fields['last_name'].widget.attrs['disabled'] = True
        self.fields['last_name'].widget.attrs['style'] = 'background-color: #e9ecef;'

            
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['name', 'email', 'phone_number', 'message']
        
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = 'Enter your name'
        self.fields['email'].widget.attrs['placeholder'] = 'Enter your email'
        self.fields['phone_number'].widget.attrs['placeholder'] = 'Enter your phone number'
        self.fields['message'].widget.attrs['placeholder'] = 'Enter your message'
        
        
class RestaurantAddressForm(forms.ModelForm):
    class Meta:
        model = RestaurantAddress
        fields = ['country', 'state', 'city', 'street', 'zip_code']
        from django import template

        register = template.Library()

        @register.filter(name='add_class')
        def add_class(field, css_class):
            return field.as_widget(attrs={"class": css_class})
        
        
class CustomPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your current password'})
    )
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your new password'})
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your confirm password'})
    )

    def __init__(self, *args, **kwargs):
        super(CustomPasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_new_password1(self):
        password1 = self.cleaned_data.get('new_password1')
        
        # Use Django's validate_password to run all registered validators, including your custom one
        try:
            validate_password(password1, self.user)
        except ValidationError as e:
            self.add_error('new_password1', e)
        
        return password1