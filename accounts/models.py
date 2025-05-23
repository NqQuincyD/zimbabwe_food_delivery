from django.contrib.auth.models import AbstractUser
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    class UserType(models.TextChoices):
        CUSTOMER = 'CUSTOMER', _('Customer')
        RESTAURANT = 'RESTAURANT', _('Restaurant Owner')
        DRIVER = 'DRIVER', _('Delivery Driver')
        ADMIN = 'ADMIN', _('Admin')
    
    user_type = models.CharField(
        max_length=10,
        choices=UserType.choices,
        default=UserType.CUSTOMER,
    )
    phone_number = PhoneNumberField(blank=True)
    profile_picture = models.ImageField(upload_to='user_images/', blank=True, null=True)
    
    def __str__(self):
        return self.email

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    default_address = models.TextField(blank=True)
    favorite_restaurants = models.ManyToManyField('restaurants.Restaurant', blank=True)
    
    def __str__(self):
        return f"{self.user.email}'s Customer Profile"

class DriverProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='driver_profile')
    id_number = models.CharField(max_length=30)
    vehicle_type = models.CharField(max_length=50)
    license_number = models.CharField(max_length=50)
    is_available = models.BooleanField(default=False)
    current_location_lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    current_location_lng = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    def __str__(self):
        return f"{self.user.email}'s Driver Profile"

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    name = models.CharField(max_length=100)  # e.g. "Home", "Work"
    street = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state_province = models.CharField(max_length=100)
    landmark = models.CharField(max_length=255, blank=True)
    is_default = models.BooleanField(default=False)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.user.email}"