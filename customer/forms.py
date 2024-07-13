from django import forms
from .models import CardDetails
import datetime

class AddressForm(forms.Form):
    country = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    city = forms.CharField(max_length=100, required=True)
    street = forms.CharField(max_length=100, required=True)
    zip_code = forms.CharField(max_length=10, required=False)
    type = forms.ChoiceField(choices=(('Home', 'Home'), ('Work', 'Work'), ('Other', 'Other')), required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    
    
class CardDetailsForm(forms.Form):
    card_number = forms.CharField(max_length=16, required=True)
    expiry_month = forms.CharField(max_length=2, required=True)
    expiry_year = forms.CharField(max_length=4, required=True)
    cvv = forms.CharField(max_length=3, required=True)
    name_on_card = forms.CharField(max_length=100, required=True)
    zip_code = forms.CharField(max_length=10, required=True)
    
    def clean_card_number(self):
        card_number = self.cleaned_data['card_number']
        if not card_number.isdigit():
            raise forms.ValidationError('Card number should contain only digits')
        return card_number
    
    class Meta:
        model = CardDetails
        fields = ['card_number', 'expiry_month', 'expiry_year', 'cvv', 'name_on_card', 'zip_code']