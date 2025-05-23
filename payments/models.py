from django.db import models
from orders.models import Order

class Payment(models.Model):
    class PaymentStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
        REFUNDED = 'REFUNDED', 'Refunded'
    
    class PaymentMethod(models.TextChoices):
        CASH = 'CASH', 'Cash on Delivery'
        ECOCASH = 'ECOCASH', 'EcoCash'
        ONEMONEY = 'ONEMONEY', 'OneMoney'
        BANK_TRANSFER = 'BANK_TRANSFER', 'Bank Transfer'
        CARD = 'CARD', 'Credit/Debit Card'
    
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=15, choices=PaymentMethod.choices)
    status = models.CharField(max_length=10, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    transaction_id = models.CharField(max_length=255, blank=True)
    payment_gateway_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.get_status_display()}"

class RestaurantPayout(models.Model):
    class PayoutStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
    
    restaurant = models.ForeignKey('restaurants.Restaurant', on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=PayoutStatus.choices, default=PayoutStatus.PENDING)
    payout_method = models.CharField(max_length=50)
    payout_details = models.JSONField(default=dict)
    transaction_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payout to {self.restaurant.name} - {self.amount}"

class DriverPayout(models.Model):
    class PayoutStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        COMPLETED = 'COMPLETED', 'Completed'
        FAILED = 'FAILED', 'Failed'
    
    driver = models.ForeignKey('accounts.User', on_delete=models.CASCADE, related_name='payouts')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=10, choices=PayoutStatus.choices, default=PayoutStatus.PENDING)
    payout_method = models.CharField(max_length=50)
    payout_details = models.JSONField(default=dict)
    transaction_id = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Payout to {self.driver.email} - {self.amount}"