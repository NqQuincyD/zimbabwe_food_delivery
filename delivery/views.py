from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.utils import timezone
from django.db import transaction
from django.http import JsonResponse
from .models import DeliveryRequest, DeliveryRating, DeliveryZone
from .forms import DeliveryRequestResponseForm, DeliveryRatingForm
from orders.models import Order, OrderTracking
from accounts.models import User, DriverProfile

@login_required
def available_orders(request):
    if request.user.user_type != User.UserType.DRIVER:
        messages.error(request, 'Only drivers can access this page')
        return redirect('home')
    
    # Get driver profile and check if available
    try:
        driver_profile = request.user.driver_profile
        if not driver_profile.is_available:
            messages.warning(request, 'You are currently marked as unavailable. Update your status to see available orders.')
    except DriverProfile.DoesNotExist:
        messages.error(request, 'You need to complete your driver profile')
        return redirect('accounts:profile')
    
    # Get orders that are ready for pickup and don't have a driver assigned
    available_orders = Order.objects.filter(
        status=Order.OrderStatus.READY_FOR_PICKUP,
        driver__isnull=True
    ).order_by('-ordered_at')
    
    # Get orders that have pending delivery requests for this driver
    pending_requests = DeliveryRequest.objects.filter(
        driver=request.user,
        status=DeliveryRequest.RequestStatus.PENDING
    )
    
    # Get active deliveries
    active_deliveries = Order.objects.filter(
        driver=request.user,
        status__in=[Order.OrderStatus.PICKED_UP, Order.OrderStatus.DELIVERING]
    )
    
    context = {
        'available_orders': available_orders,
        'pending_requests': pending_requests,
        'active_deliveries': active_deliveries,
    }
    
    return render(request, 'delivery/available_orders.html', context)

@login_required
def request_delivery(request, order_id):
    if request.user.user_type != User.UserType.DRIVER:
        messages.error(request, 'Only drivers can request deliveries')
        return redirect('home')
    
    order = get_object_or_404(Order, id=order_id, status=Order.OrderStatus.READY_FOR_PICKUP, driver__isnull=True)
    
    # Check if driver already has a pending request for this order
    existing_request = DeliveryRequest.objects.filter(
        order=order,
        driver=request.user,
        status=DeliveryRequest.RequestStatus.PENDING
    ).exists()
    
    if existing_request:
        messages.warning(request, 'You already have a pending request for this order')
    else:
        DeliveryRequest.objects.create(
            order=order,
            driver=request.user,
            status=DeliveryRequest.RequestStatus.PENDING
        )
        messages.success(request, 'Delivery request submitted')
    
    return redirect('delivery:available_orders')

@login_required
def accept_delivery_request(request, request_id):
    delivery_request = get_object_or_404(DeliveryRequest, id=request_id)
    order = delivery_request.order
    
    # Verify the current user is the restaurant owner
    if request.user != order.restaurant.owner:
        messages.error(request, 'You are not authorized to accept this request')
        return redirect('orders:order_detail', pk=order.id)
    
    # Verify the order doesn't already have a driver
    if order.driver:
        messages.error(request, 'This order already has a driver assigned')
        return redirect('orders:order_detail', pk=order.id)
    
    with transaction.atomic():
        # Assign driver to order
        order.driver = delivery_request.driver
        order.save()
        
        # Update delivery request status
        delivery_request.status = DeliveryRequest.RequestStatus.ACCEPTED
        delivery_request.responded_at = timezone.now()
        delivery_request.save()
        
        # Mark other pending requests for this order as expired
        DeliveryRequest.objects.filter(
            order=order,
            status=DeliveryRequest.RequestStatus.PENDING
        ).exclude(id=delivery_request.id).update(
            status=DeliveryRequest.RequestStatus.EXPIRED,
            responded_at=timezone.now()
        )
        
        # Create tracking entry
        OrderTracking.objects.create(
            order=order,
            status=order.status,
            note=f'Delivery assigned to {delivery_request.driver.get_full_name()}'
        )
    
    messages.success(request, 'Delivery request accepted')
    return redirect('orders:order_detail', pk=order.id)

@login_required
def decline_delivery_request(request, request_id):
    delivery_request = get_object_or_404(DeliveryRequest, id=request_id)
    order = delivery_request.order
    
    # Verify the current user is the restaurant owner
    if request.user != order.restaurant.owner:
        messages.error(request, 'You are not authorized to decline this request')
        return redirect('orders:order_detail', pk=order.id)
    
    # Update delivery request status
    delivery_request.status = DeliveryRequest.RequestStatus.DECLINED
    delivery_request.responded_at = timezone.now()
    delivery_request.save()
    
    messages.success(request, 'Delivery request declined')
    return redirect('orders:order_detail', pk=order.id)

@login_required
def rate_delivery(request, order_id):
    order = get_object_or_404(Order, id=order_id, status=Order.OrderStatus.DELIVERED)
    
    # Verify the current user is the customer for this order
    if request.user != order.customer:
        messages.error(request, 'You can only rate your own orders')
        return redirect('orders:order_detail', pk=order.id)
    
    # Check if delivery already rated
    existing_rating = DeliveryRating.objects.filter(order=order).exists()
    if existing_rating:
        messages.warning(request, 'You have already rated this delivery')
        return redirect('orders:order_detail', pk=order.id)
    
    if request.method == 'POST':
        form = DeliveryRatingForm(request.POST)
        if form.is_valid():
            rating = form.save(commit=False)
            rating.order = order
            rating.save()
            
            messages.success(request, 'Thank you for rating your delivery!')
            return redirect('orders:order_detail', pk=order.id)
    else:
        form = DeliveryRatingForm()
    
    context = {
        'form': form,
        'order': order
    }
    
    return render(request, 'delivery/rate_delivery.html', context)

@login_required
def update_driver_location(request):
    if request.user.user_type != User.UserType.DRIVER:
        return JsonResponse({'error': 'Only drivers can update location'}, status=403)
    
    if request.method == 'POST':
        try:
            latitude = float(request.POST.get('latitude'))
            longitude = float(request.POST.get('longitude'))
            
            # Update driver's location
            driver_profile = request.user.driver_profile
            driver_profile.current_location_lat = latitude
            driver_profile.current_location_lng = longitude
            driver_profile.save()
            
            # Update tracking for any active delivery
            active_orders = Order.objects.filter(
                driver=request.user,
                status__in=[Order.OrderStatus.PICKED_UP, Order.OrderStatus.DELIVERING]
            )
            
            for order in active_orders:
                OrderTracking.objects.create(
                    order=order,
                    status=order.status,
                    latitude=latitude,
                    longitude=longitude,
                    note='Driver location updated'
                )
            
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)
    
    return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)