from django.contrib import admin
from .models import Restaurant, Category, MenuItem, RestaurantHours, MenuItemOption, MenuItemOptionChoice

@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ['name', 'owner', 'city', 'is_approved', 'is_open', 'created_at']
    list_filter = ['is_approved', 'is_open', 'city']
    search_fields = ['name', 'owner__username', 'owner__email', 'city']
    actions = ['approve_restaurants', 'unapprove_restaurants']
    
    def approve_restaurants(self, request, queryset):
        queryset.update(is_approved=True)
    approve_restaurants.short_description = "Approve selected restaurants"
    
    def unapprove_restaurants(self, request, queryset):
        queryset.update(is_approved=False)
    unapprove_restaurants.short_description = "Unapprove selected restaurants"

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ['name', 'restaurant', 'category', 'price', 'is_available']
    list_filter = ['is_available', 'is_vegetarian', 'is_vegan', 'is_featured', 'category']
    search_fields = ['name', 'restaurant__name']

@admin.register(RestaurantHours)
class RestaurantHoursAdmin(admin.ModelAdmin):
    list_display = ['restaurant', 'day', 'opening_time', 'closing_time', 'is_closed']
    list_filter = ['day', 'is_closed']
    search_fields = ['restaurant__name']

@admin.register(MenuItemOption)
class MenuItemOptionAdmin(admin.ModelAdmin):
    list_display = ['name', 'menu_item']
    search_fields = ['name', 'menu_item__name']

@admin.register(MenuItemOptionChoice)
class MenuItemOptionChoiceAdmin(admin.ModelAdmin):
    list_display = ['value', 'option', 'additional_price']
    search_fields = ['value', 'option__name']
