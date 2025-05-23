from django.conf import settings
from django.shortcuts import resolve_url
from allauth.account.adapter import DefaultAccountAdapter
from .models import User, CustomerProfile, DriverProfile

class CustomAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        """Redirect users to different dashboards based on their user type"""
        user = request.user
        
        if user.user_type == User.UserType.CUSTOMER:
            return resolve_url('customer_dashboard')
        elif user.user_type == User.UserType.RESTAURANT:
            return resolve_url('restaurant_dashboard')
        elif user.user_type == User.UserType.DRIVER:
            return resolve_url('driver_dashboard')
        else:
            # Default fallback
            return resolve_url(settings.LOGIN_REDIRECT_URL)
            
    def save_user(self, request, user, form, commit=True):
        """Create the appropriate profile when a user signs up"""
        user = super().save_user(request, user, form, commit=False)
        user.user_type = User.UserType.CUSTOMER  # Default to customer for now
        
        if commit:
            user.save()
            # Create the customer profile
            CustomerProfile.objects.create(user=user)
            
        return user