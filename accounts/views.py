from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DetailView, ListView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User, CustomerProfile, DriverProfile, Address
from .forms import (
    CustomUserCreationForm, CustomUserChangeForm, ProfilePictureForm,
    CustomerProfileForm, DriverProfileForm, AddressForm
)

class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('account_login') 
    template_name = 'accounts/signup.html'
    
    def form_valid(self, form):
        response = super().form_valid(form)
        user_type = form.cleaned_data.get('user_type')
        
        if user_type == User.UserType.CUSTOMER:
            CustomerProfile.objects.create(user=self.object)
        elif user_type == User.UserType.DRIVER:
            DriverProfile.objects.create(user=self.object)
            
        messages.success(self.request, 'Account created successfully. Please login.')
        return response

@login_required
def profile_view(request):
    user = request.user
    
    # Create profile if it doesn't exist
    if user.user_type == User.UserType.CUSTOMER:
        customer_profile, created = CustomerProfile.objects.get_or_create(user=user)
    elif user.user_type == User.UserType.DRIVER:
        driver_profile, created = DriverProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user_form = CustomUserChangeForm(request.POST, instance=user)
        profile_picture_form = ProfilePictureForm(request.POST, request.FILES, instance=user)
        
        if user.user_type == User.UserType.CUSTOMER:
            profile_form = CustomerProfileForm(request.POST, instance=user.customer_profile)
        elif user.user_type == User.UserType.DRIVER:
            profile_form = DriverProfileForm(request.POST, instance=user.driver_profile)
        else:
            profile_form = None
            
        if user_form.is_valid() and profile_picture_form.is_valid() and (profile_form is None or profile_form.is_valid()):
            user_form.save()
            profile_picture_form.save()
            
            if profile_form:
                profile_form.save()
                
            messages.success(request, 'Profile updated successfully.')
            return redirect('accounts:profile')
    else:
        user_form = CustomUserChangeForm(instance=user)
        profile_picture_form = ProfilePictureForm(instance=user)
        
        if user.user_type == User.UserType.CUSTOMER:
            profile_form = CustomerProfileForm(instance=user.customer_profile)
        elif user.user_type == User.UserType.DRIVER:
            profile_form = DriverProfileForm(instance=user.driver_profile)
        else:
            profile_form = None
    
    context = {
        'user_form': user_form,
        'profile_picture_form': profile_picture_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile.html', context)

class AddressListView(LoginRequiredMixin, ListView):
    model = Address
    template_name = 'accounts/address_list.html'
    context_object_name = 'addresses'
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)

class AddressCreateView(LoginRequiredMixin, CreateView):
    model = Address
    form_class = AddressForm
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('accounts:address_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        
        # If this is set as default, unset others
        if form.cleaned_data.get('is_default'):
            Address.objects.filter(user=self.request.user, is_default=True).update(is_default=False)
            
        messages.success(self.request, 'Address added successfully.')
        return super().form_valid(form)

class AddressUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Address
    form_class = AddressForm
    template_name = 'accounts/address_form.html'
    success_url = reverse_lazy('accounts:address_list')
    
    def test_func(self):
        address = self.get_object()
        return address.user == self.request.user
    
    def form_valid(self, form):
        # If this is set as default, unset others
        if form.cleaned_data.get('is_default'):
            Address.objects.filter(user=self.request.user, is_default=True).exclude(pk=self.object.pk).update(is_default=False)
            
        messages.success(self.request, 'Address updated successfully.')
        return super().form_valid(form)

class AddressDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Address
    template_name = 'accounts/address_confirm_delete.html'
    success_url = reverse_lazy('accounts:address_list')
    
    def test_func(self):
        address = self.get_object()
        return address.user == self.request.user
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Address deleted successfully.')
        return super().delete(request, *args, **kwargs)

@login_required
def driver_toggle_availability(request):
    if request.user.user_type != User.UserType.DRIVER:
        messages.error(request, 'You do not have permission to access this page.')
        return redirect('home')
    
    driver_profile = request.user.driver_profile
    driver_profile.is_available = not driver_profile.is_available
    driver_profile.save()
    
    status = 'available' if driver_profile.is_available else 'unavailable'
    messages.success(request, f'You are now {status} for deliveries.')
    return redirect('accounts:profile')

class DriverDashboardView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    template_name = 'accounts/driver_dashboard.html'
    context_object_name = 'delivery_requests'
    
    def test_func(self):
        return self.request.user.user_type == User.UserType.DRIVER
    
    def get_queryset(self):
        return self.request.user.delivery_requests.filter(status='PENDING')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['active_deliveries'] = self.request.user.deliveries.filter(
            status__in=['PICKED_UP', 'DELIVERING']
        )
        context['completed_deliveries'] = self.request.user.deliveries.filter(
            status='DELIVERED'
        ).order_by('-delivered_at')[:10]
        return context