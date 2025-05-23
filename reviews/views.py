from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from django.urls import reverse

from .models import RestaurantReview, MenuItemReview, DriverReview
from .forms import RestaurantReviewForm, MenuItemReviewForm, DriverReviewForm
from restaurants.models import Restaurant, MenuItem
from orders.models import Order
from accounts.models import User

@login_required
def restaurant_review(request, restaurant_id):
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    # Check if user has ordered from this restaurant
    has_ordered = Order.objects.filter(
        customer=request.user,
        restaurant=restaurant,
        status=Order.OrderStatus.DELIVERED
    ).exists()
    
    if not has_ordered:
        messages.warning(request, 'You can only review restaurants you have ordered from')
        return redirect('restaurant_detail', slug=restaurant.slug)
    
    # Get user's completed orders from this restaurant
    orders = Order.objects.filter(
        customer=request.user,
        restaurant=restaurant,
        status=Order.OrderStatus.DELIVERED
    ).order_by('-delivered_at')
    
    if request.method == 'POST':
        form = RestaurantReviewForm(request.POST)
        if form.is_valid():
            # Check if user already reviewed this restaurant for this order
            order_id = request.POST.get('order_id')
            if order_id:
                order = get_object_or_404(Order, id=order_id, customer=request.user)
                existing_review = RestaurantReview.objects.filter(
                    restaurant=restaurant,
                    user=request.user,
                    order=order
                ).exists()
                
                if existing_review:
                    messages.warning(request, 'You have already reviewed this restaurant for this order')
                    return redirect('restaurant_detail', slug=restaurant.slug)
                
                review = form.save(commit=False)
                review.restaurant = restaurant
                review.user = request.user
                review.order = order
                review.save()
            else:
                # No specific order, check if user has reviewed the restaurant
                existing_review = RestaurantReview.objects.filter(
                    restaurant=restaurant,
                    user=request.user,
                    order__isnull=True
                ).exists()
                
                if existing_review:
                    messages.warning(request, 'You have already reviewed this restaurant')
                    return redirect('restaurant_detail', slug=restaurant.slug)
                
                review = form.save(commit=False)
                review.restaurant = restaurant
                review.user = request.user
                review.save()
            
            # Update restaurant average rating
            avg_rating = RestaurantReview.objects.filter(restaurant=restaurant).aggregate(Avg('rating'))['rating__avg']
            restaurant.average_rating = avg_rating or 0.0
            restaurant.save()
            
            messages.success(request, 'Thank you for your review!')
            return redirect('restaurant_detail', slug=restaurant.slug)
    else:
        form = RestaurantReviewForm()
    
    context = {
        'form': form,
        'restaurant': restaurant,
        'orders': orders
    }
    
    return render(request, 'reviews/restaurant_review.html', context)

@login_required
def menu_item_review(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id)
    
    # Check if user has ordered this item
    has_ordered = OrderItem.objects.filter(
        order__customer=request.user,
        order__status=Order.OrderStatus.DELIVERED,
        menu_item=menu_item
    ).exists()
    
    if not has_ordered:
        messages.warning(request, 'You can only review items you have ordered')
        return redirect('restaurant_detail', slug=menu_item.restaurant.slug)
    
    # Get user's orders containing this item
    from orders.models import OrderItem
    orders_with_item = Order.objects.filter(
        customer=request.user,
        status=Order.OrderStatus.DELIVERED,
        items__menu_item=menu_item
    ).order_by('-delivered_at')
    
    if request.method == 'POST':
        form = MenuItemReviewForm(request.POST)
        if form.is_valid():
            # Check if user already reviewed this item for this order
            order_id = request.POST.get('order_id')
            if order_id:
                order = get_object_or_404(Order, id=order_id, customer=request.user)
                existing_review = MenuItemReview.objects.filter(
                    menu_item=menu_item,
                    user=request.user,
                    order=order
                ).exists()
                
                if existing_review:
                    messages.warning(request, 'You have already reviewed this item for this order')
                    return redirect('restaurant_detail', slug=menu_item.restaurant.slug)
                
                review = form.save(commit=False)
                review.menu_item = menu_item
                review.user = request.user
                review.order = order
                review.save()
            else:
                # No specific order, check if user has reviewed the item
                existing_review = MenuItemReview.objects.filter(
                    menu_item=menu_item,
                    user=request.user,
                    order__isnull=True
                ).exists()
                
                if existing_review:
                    messages.warning(request, 'You have already reviewed this item')
                    return redirect('restaurant_detail', slug=menu_item.restaurant.slug)
                
                review = form.save(commit=False)
                review.menu_item = menu_item
                review.user = request.user
                review.save()
            
            messages.success(request, 'Thank you for your review!')
            return redirect('restaurant_detail', slug=menu_item.restaurant.slug)
    else:
        form = MenuItemReviewForm()
    
    context = {
        'form': form,
        'menu_item': menu_item,
        'orders': orders_with_item
    }
    
    return render(request, 'reviews/menu_item_review.html', context)

@login_required
def driver_review(request, order_id):
    order = get_object_or_404(
        Order, 
        id=order_id, 
        customer=request.user, 
        status=Order.OrderStatus.DELIVERED,
        driver__isnull=False
    )
    
    # Check if user already reviewed this driver for this order
    existing_review = DriverReview.objects.filter(order=order).exists()
    if existing_review:
        messages.warning(request, 'You have already reviewed this delivery')
        return redirect('order_detail', pk=order.id)
    
    if request.method == 'POST':
        form = DriverReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.driver = order.driver
            review.user = request.user
            review.order = order
            review.save()
            
            messages.success(request, 'Thank you for rating your driver!')
            return redirect('order_detail', pk=order.id)
    else:
        form = DriverReviewForm()
    
    context = {
        'form': form,
        'order': order,
        'driver': order.driver
    }
    
    return render(request, 'reviews/driver_review.html', context)