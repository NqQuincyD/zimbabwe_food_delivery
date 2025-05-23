from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from phonenumber_field.formfields import PhoneNumberField
from .models import User, CustomerProfile, DriverProfile, Address
from allauth.account.forms import SignupForm

class CustomUserCreationForm(UserCreationForm):
    phone_number = PhoneNumberField(required=True)
    
    class Meta:
        model = User
        fields = ('email', 'username', 'phone_number', 'first_name', 'last_name', 'user_type')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'phone_number', 'first_name', 'last_name')

class ProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('profile_picture',)
        
class CustomerProfileForm(forms.ModelForm):
    class Meta:
        model = CustomerProfile
        fields = ('default_address',)

class DriverProfileForm(forms.ModelForm):
    class Meta:
        model = DriverProfile
        fields = ('id_number', 'vehicle_type', 'license_number')

class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ('name', 'street', 'city', 'state_province', 'landmark', 'is_default')