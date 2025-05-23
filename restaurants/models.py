from django.db import models
from django.conf import settings
from phonenumber_field.modelfields import PhoneNumberField
from django.utils.text import slugify

class Restaurant(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='restaurants')
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    logo = models.ImageField(upload_to='restaurant_images/')
    cover_photo = models.ImageField(upload_to='restaurant_images/', blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=50)
    phone_number = PhoneNumberField()
    email = models.EmailField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_open = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    delivery_radius = models.DecimalField(max_digits=5, decimal_places=2, help_text="Radius in kilometers")
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class RestaurantHours(models.Model):
    DAYS_OF_WEEK = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='hours')
    day = models.IntegerField(choices=DAYS_OF_WEEK)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    is_closed = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('restaurant', 'day')
    
    def __str__(self):
        return f"{self.restaurant.name} - {self.get_day_display()}"

class Category(models.Model):
    name = models.CharField(max_length=50)
    description = models.TextField(blank=True)
    
    class Meta:
        verbose_name_plural = "Categories"
    
    def __str__(self):
        return self.name

class MenuItem(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='menu_items')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='items')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    preparation_time = models.PositiveIntegerField(help_text="Preparation time in minutes", default=30)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"

class MenuItemOption(models.Model):
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='options')
    name = models.CharField(max_length=50)  # e.g., "Size", "Spice Level"
    
    def __str__(self):
        return f"{self.name} - {self.menu_item.name}"

class MenuItemOptionChoice(models.Model):
    option = models.ForeignKey(MenuItemOption, on_delete=models.CASCADE, related_name='choices')
    value = models.CharField(max_length=50)  # e.g., "Small", "Medium", "Large"
    additional_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.value} (+${self.additional_price})"