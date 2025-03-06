from django import forms

class OTPForm(forms.Form):
    otp_code = forms.CharField(max_length=6, widget=forms.TextInput(attrs={'placeholder': 'Enter OTP Code'}))