from django import forms

class AddressForm(forms.Form):
    country = forms.CharField(max_length=100, required=True)
    state = forms.CharField(max_length=100, required=True)
    city = forms.CharField(max_length=100, required=True)
    street = forms.CharField(max_length=100, required=True)
    zip_code = forms.CharField(max_length=10, required=False)
    type = forms.ChoiceField(choices=(('Home', 'Home'), ('Work', 'Work'), ('Other', 'Other')), required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    
    