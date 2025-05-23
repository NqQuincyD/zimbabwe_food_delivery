from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db import transaction
from django.core.exceptions import PermissionDenied
from decimal import Decimal

from .models import Order, OrderItem, OrderItemOptionChoice, OrderTracking
from .forms import OrderForm, OrderItemForm, OrderStatusUpdateForm
from restaurants.models import Restaurant, MenuItem, MenuItemOptionChoice
from accounts.models import Address, User
from delivery.models import DeliveryRequest

class CartView(LoginRequiredMixin, ListView):
    template_name = 'orders/cart.html'
    context_object_name = 'cart_items'
    
    def get_queryset(self):
        # This should retrieve cart items from the session
        cart = self.request.session.get('cart', {})
        cart_items = []
        
        for item_id, item_data in cart.items():
            menu_item = MenuItem.objects.get(id=item_data['menu_item_id'])
            cart_items.append({
                'id': item_id,
                'menu_item': menu_item,
                'quantity': item_data['quantity'],
                'special_instructions': item_data.get('special_instructions', ''),
                'option_choices': [
                    MenuItemOptionChoice.objects.get(id=choice_id)
                    for choice_id in item_data.get('option_choices', [])
                ],
                'total_price': menu_item.price * Decimal(item_data['quantity']) + sum(
                    MenuItemOptionChoice.objects.get(id=choice_id).additional_price
                    for choice_id in item_data.get('option_choices', [])
                )
            })
        
        return cart_items
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Calculate subtotal, delivery fee, and total
        cart_items = context['cart_items']
        subtotal = sum(item['total_price'] for item in cart_items)
        
        # Get restaurant from first item if cart not empty
        restaurant = None
        if cart_items:
            restaurant = cart_items[0]['menu_item'].restaurant
            context['restaurant'] = restaurant
        
        # Default delivery fee
        delivery_fee = Decimal('0.00')
        if restaurant:
            # This should be calculated based on distance, but using fixed fee for simplicity
            delivery_fee = Decimal('5.00')
        
        context['subtotal'] = subtotal
        context['delivery_fee'] = delivery_fee
        context['total'] = subtotal + delivery_fee
        
        # Get user addresses
        context['addresses'] = Address.objects.filter(user=self.request.user)
        
        return context

@login_required
def add_to_cart(request, menu_item_id):
    if request.method == 'POST':
        menu_item = get_object_or_404(MenuItem, id=menu_item_id)
        
        # Initialize cart if it doesn't exist
        if 'cart' not in request.session:
            request.session['cart'] = {}
            request.session['cart_restaurant_id'] = menu_item.restaurant.id
        
        # Check if adding from a different restaurant
        elif 'cart_restaurant_id' in request.session and request.session['cart_restaurant_id'] != menu_item.restaurant.id:
            messages.warning(request, 'You cannot order from multiple restaurants at once. Please clear your cart first.')
            return redirect('restaurants:restaurant_detail', slug=menu_item.restaurant.slug)
        
        # Get form data
        form = OrderItemForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            special_instructions = form.cleaned_data['special_instructions']
            
            # Get selected options
            option_choices = request.POST.getlist('option_choices')
            
            # Create unique item ID
            import uuid
            item_id = str(uuid.uuid4())
            
            # Add to cart
            request.session['cart'][item_id] = {
                'menu_item_id': menu_item.id,
                'quantity': quantity,
                'special_instructions': special_instructions,
                'option_choices': option_choices,
            }
            request.session.modified = True
            
            messages.success(request, f'{menu_item.name} added to cart')
            return redirect('restaurants:restaurant_detail', slug=menu_item.restaurant.slug)
        else:
            messages.error(request, 'Error adding item to cart')
            return redirect('restaurants:restaurant_detail', slug=menu_item.restaurant.slug)
    
    return redirect('restaurants:restaurant_list')

@login_required
def remove_from_cart(request, item_id):
    if 'cart' in request.session and item_id in request.session['cart']:
        del request.session['cart'][item_id]
        request.session.modified = True
        
        # If cart is empty, remove restaurant ID
        if not request.session['cart']:
            if 'cart_restaurant_id' in request.session:
                del request.session['cart_restaurant_id']
        
        messages.success(request, 'Item removed from cart')
    
    return redirect('cart')

@login_required
def clear_cart(request):
    if 'cart' in request.session:
        del request.session['cart']
    if 'cart_restaurant_id' in request.session:
        del request.session['cart_restaurant_id']
    
    messages.success(request, 'Cart cleared')
    return redirect('cart')

@login_required
def checkout(request):
    # Ensure cart is not empty
    if 'cart' not in request.session or not request.session['cart']:
        messages.warning(request, 'Your cart is empty')
        return redirect('cart')
    
    # Get restaurant from first item
    restaurant_id = request.session.get('cart_restaurant_id')
    restaurant = get_object_or_404(Restaurant, id=restaurant_id)
    
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                # Create the order
                order = form.save(commit=False)
                order.customer = request.user
                order.restaurant = restaurant
                
                # Calculate prices
                cart_items = []
                subtotal = Decimal('0.00')
                
                for item_id, item_data in request.session['cart'].items():
                    menu_item = MenuItem.objects.get(id=item_data['menu_item_id'])
                    quantity = item_data['quantity']
                    
                    # Calculate item price
                    item_price = menu_item.price * Decimal(quantity)
                    
                    # Add option prices
                    option_choices = [
                        MenuItemOptionChoice.objects.get(id=choice_id)
                        for choice_id in item_data.get('option_choices', [])
                    ]
                    options_price = sum(choice.additional_price for choice in option_choices)
                    
                    # Add to cart items
                    cart_items.append({
                        'menu_item': menu_item,
                        'quantity': quantity,
                        'special_instructions': item_data.get('special_instructions', ''),
                        'option_choices': option_choices,
                        'price': item_price + options_price
                    })
                    
                    # Add to subtotal
                    subtotal += item_price + options_price
                
                # Set prices
                delivery_fee = Decimal('5.00')  # Should be calculated based on distance
                order.total_price = subtotal + delivery_fee
                order.delivery_fee = delivery_fee
                
                # Set payment method (from form)
                order.payment_method = request.POST.get('payment_method', 'CASH')
                
                # Save order
                order.save()
                
                # Create order items
                for item in cart_items:
                    order_item = OrderItem.objects.create(
                        order=order,
                        menu_item=item['menu_item'],
                        quantity=item['quantity'],
                        price=item['price'],
                        special_instructions=item['special_instructions']
                    )
                    
                    # Create option choices
                    for option_choice in item['option_choices']:
                        OrderItemOptionChoice.objects.create(
                            order_item=order_item,
                            option_choice=option_choice
                        )
                
                # Create initial tracking entry
                OrderTracking.objects.create(
                    order=order,
                    status=Order.OrderStatus.PENDING,
                    note='Order placed'
                )
                
                # Clear the cart
                del request.session['cart']
                if 'cart_restaurant_id' in request.session:
                    del request.session['cart_restaurant_id']
                
                messages.success(request, 'Order placed successfully!')
                return redirect('orders:order_detail', pk=order.id)
    else:
        # Initial form
        default_address = None
        try:
            default_address = Address.objects.get(user=request.user, is_default=True)
        except Address.DoesNotExist:
            # Try to get any address
            addresses = Address.objects.filter(user=request.user)
            if addresses.exists():
                default_address = addresses.first()
        
        form = OrderForm(initial={'delivery_address': default_address})
    
    # Calculate cart items and totals
    cart_items = []
    subtotal = Decimal('0.00')
    
    for item_id, item_data in request.session['cart'].items():
        menu_item = MenuItem.objects.get(id=item_data['menu_item_id'])
        quantity = item_data['quantity']
        
        # Calculate item price
        item_price = menu_item.price * Decimal(quantity)
        
        # Add option prices
        option_choices = [
            MenuItemOptionChoice.objects.get(id=choice_id)
            for choice_id in item_data.get('option_choices', [])
        ]
        options_price = sum(choice.additional_price for choice in option_choices)
        
        # Add to cart items
        cart_items.append({
            'id': item_id,
            'menu_item': menu_item,
            'quantity': quantity,
            'special_instructions': item_data.get('special_instructions', ''),
            'option_choices': option_choices,
            'total_price': item_price + options_price
        })
        
        # Add to subtotal
        subtotal += item_price + options_price
    
    # Set prices
    delivery_fee = Decimal('5.00')  # Should be calculated based on distance
    total = subtotal + delivery_fee
    
    context = {
        'form': form,
        'cart_items': cart_items,
        'restaurant': restaurant,
        'subtotal': subtotal,
        'delivery_fee': delivery_fee,
        'total': total,
        'addresses': Address.objects.filter(user=request.user)
    }
    
    return render(request, 'orders/checkout.html', context)

class OrderListView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'orders/order_list.html'
    context_object_name = 'orders'
    paginate_by = 10
    
    def get_queryset(self):
        user = self.request.user
        
        if user.user_type == User.UserType.CUSTOMER:
            return Order.objects.filter(customer=user).order_by('-ordered_at')
        elif user.user_type == User.UserType.RESTAURANT:
            return Order.objects.filter(restaurant__owner=user).order_by('-ordered_at')
        elif user.user_type == User.UserType.DRIVER:
            return Order.objects.filter(driver=user).order_by('-ordered_at')
        else:
            return Order.objects.all().order_by('-ordered_at')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['user_type'] = self.request.user.user_type
        return context

class OrderDetailView(LoginRequiredMixin, DetailView):
    model = Order
    template_name = 'orders/order_detail.html'
    context_object_name = 'order'
    
    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        user = self.request.user
        
        # Check if user has permission to view this order
        if user.user_type == User.UserType.CUSTOMER and obj.customer != user:
            raise PermissionDenied
        elif user.user_type == User.UserType.RESTAURANT and obj.restaurant.owner != user:
            raise PermissionDenied
        elif user.user_type == User.UserType.DRIVER and obj.driver != user:
            # Allow drivers to see orders assigned to them
            if not DeliveryRequest.objects.filter(order=obj, driver=user).exists():
                raise PermissionDenied
        
        return obj
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracking'] = OrderTracking.objects.filter(order=self.object).order_by('timestamp')
        context['user_type'] = self.request.user.user_type
        
        # For restaurant owners, add status update form
        if self.request.user.user_type == User.UserType.RESTAURANT:
            context['status_form'] = OrderStatusUpdateForm(instance=self.object)
        
        return context

@login_required
def update_order_status(request, pk):
    order = get_object_or_404(Order, pk=pk)
    
    # Check permissions
    if request.user.user_type == User.UserType.RESTAURANT and order.restaurant.owner != request.user:
        raise PermissionDenied
    elif request.user.user_type == User.UserType.DRIVER and order.driver != request.user:
        raise PermissionDenied
    
    if request.method == 'POST':
        form = OrderStatusUpdateForm(request.POST, instance=order)
        if form.is_valid():
            new_status = form.cleaned_data['status']
            old_status = order.status
            
            # Validate status transitions
            valid_transition = False
            
            if request.user.user_type == User.UserType.RESTAURANT:
                # Restaurant can only change to these statuses
                if new_status in [
                    Order.OrderStatus.ACCEPTED, 
                    Order.OrderStatus.PREPARING, 
                    Order.OrderStatus.READY_FOR_PICKUP,
                    Order.OrderStatus.CANCELLED
                ]:
                    valid_transition = True
            elif request.user.user_type == User.UserType.DRIVER:
                # Driver can only change to these statuses
                if new_status in [Order.OrderStatus.PICKED_UP, Order.OrderStatus.DELIVERING, Order.OrderStatus.DELIVERED]:
                    valid_transition = True
            
            if valid_transition:
                # Update order status
                order.status = new_status
                
                # Update timestamps based on status
                if new_status == Order.OrderStatus.ACCEPTED:
                    order.accepted_at = timezone.now()
                elif new_status == Order.OrderStatus.PICKED_UP:
                    order.picked_up_at = timezone.now()
                elif new_status == Order.OrderStatus.DELIVERED:
                    order.delivered_at = timezone.now()
                elif new_status == Order.OrderStatus.CANCELLED:
                    order.cancelled_at = timezone.now()
                
                order.save()
                
                # Create tracking entry
                OrderTracking.objects.create(
                    order=order,
                    status=new_status,
                    note=f'Status updated from {old_status} to {new_status}'
                )
                
                messages.success(request, f'Order status updated to {new_status}')
            else:
                messages.error(request, 'Invalid status transition')
        else:
            messages.error(request, 'Invalid form data')
    
    return redirect('orders:order_detail', pk=order.pk)