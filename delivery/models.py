from django.db import models
from django.conf import settings
from orders.models import Order

class DeliveryZone(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    base_fee = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.name

class DeliveryRequest(models.Model):
    class RequestStatus(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        ACCEPTED = 'ACCEPTED', 'Accepted'
        DECLINED = 'DECLINED', 'Declined'
        EXPIRED = 'EXPIRED', 'Expired'
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='delivery_requests')
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='delivery_requests')
    status = models.CharField(max_length=10, choices=RequestStatus.choices, default=RequestStatus.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Delivery Request for Order #{self.order.id} to {self.driver.email}"

class DeliveryRating(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery_rating')
    rating = models.PositiveSmallIntegerField(help_text="Rating from 1 to 5")
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Delivery Rating for Order #{self.order.id}"