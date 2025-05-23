from django.db import models
from django.conf import settings
from restaurants.models import Restaurant, MenuItem, MenuItemOptionChoice

class Order(models.Model):
    class OrderStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        PREPARING = 'PREPARING', 'Preparing'
        READY_FOR_PICKUP = 'READY_FOR_PICKUP', 'Ready for Pickup'
        PICKED_UP = 'PICKED_UP', 'Picked Up'
        DELIVERING = 'DELIVERING', 'Delivering'
        DELIVERED = 'DELIVERED', 'Delivered'
        CANCELLED = 'CANCELLED', 'Cancelled'
    
    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='orders')
    driver = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='deliveries'
    )
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_fee = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_address = models.ForeignKey(
        'accounts.Address', 
        on_delete=models.SET_NULL, 
        null=True, 
        related_name='orders'
    )
    delivery_instructions = models.TextField(blank=True)
    is_paid = models.BooleanField(default=False)
    payment_method = models.CharField(max_length=50, blank=True)
    estimated_delivery_time = models.DateTimeField(null=True, blank=True)
    ordered_at = models.DateTimeField(auto_now_add=True)
    accepted_at = models.DateTimeField(null=True, blank=True)
    prepared_at = models.DateTimeField(null=True, blank=True)
    picked_up_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer.email}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price at time of order
    special_instructions = models.TextField(blank=True)
    
    def __str__(self):
        return f"{self.quantity}x {self.menu_item.name}"

class OrderItemOptionChoice(models.Model):
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='selected_options')
    option_choice = models.ForeignKey(MenuItemOptionChoice, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.order_item} - {self.option_choice.option.name}: {self.option_choice.value}"

class OrderTracking(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking_updates')
    status = models.CharField(max_length=20, choices=Order.OrderStatus.choices)
    timestamp = models.DateTimeField(auto_now_add=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    note = models.TextField(blank=True)
    
    def __str__(self):
        return f"Order #{self.order.id} - {self.status} at {self.timestamp}"