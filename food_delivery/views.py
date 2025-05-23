from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from accounts.models import User

def home(request):
    """Home page view"""
    context = {}
    return render(request, 'home.html', context)

def about(request):
    """About page view"""
    return render(request, 'about.html')

def contact(request):
    """Contact page view"""
    return render(request, 'contact.html')

def terms(request):
    """Terms of service view"""
    return render(request, 'terms.html')

def privacy(request):
    """Privacy policy view"""
    return render(request, 'privacy.html')

@login_required
def customer_dashboard(request):
    """Dashboard for customers"""
    if request.user.user_type != User.UserType.CUSTOMER:
        return redirect('home')
    return render(request, 'accounts/customer_dashboard.html')

@login_required
def restaurant_dashboard(request):
    """Dashboard for restaurant owners"""
    if request.user.user_type != User.UserType.RESTAURANT:
        return redirect('home')
    return render(request, 'accounts/restaurant_dashboard.html')

@login_required
def driver_dashboard(request):
    """Dashboard for delivery drivers"""
    if request.user.user_type != User.UserType.DRIVER:
        return redirect('home')
    return render(request, 'accounts/driver_dashboard.html')