from django.db import models
from django.conf import settings
from restaurants.models import Restaurant, MenuItem
from orders.models import Order

class RestaurantReview(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(help_text="Rating from 1 to 5")
    comment = models.TextField(blank=True)
    food_rating = models.PositiveSmallIntegerField(help_text="Food Rating from 1 to 5")
    service_rating = models.PositiveSmallIntegerField(help_text="Service Rating from 1 to 5")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('restaurant', 'user', 'order')
    
    def __str__(self):
        return f"Review for {self.restaurant.name} by {self.user.email}"

class MenuItemReview(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    rating = models.PositiveSmallIntegerField(help_text="Rating from 1 to 5")
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('menu_item', 'user', 'order')
    
    def __str__(self):
        return f"Review for {self.menu_item.name} by {self.user.email}"

class DriverReview(models.Model):
    driver = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_reviews')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_driver_reviews')
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='driver_review')
    rating = models.PositiveSmallIntegerField(help_text="Rating from 1 to 5")
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review for Driver {self.driver.email} by {self.user.email}"