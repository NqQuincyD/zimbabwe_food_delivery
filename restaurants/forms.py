from django import forms
from .models import Restaurant, Category, MenuItem, MenuItemOption, MenuItemOptionChoice, RestaurantHours

class RestaurantForm(forms.ModelForm):
    class Meta:
        model = Restaurant
        fields = (
            'name', 'description', 'logo', 'cover_photo', 'address', 'city',
            'phone_number', 'email', 'latitude', 'longitude', 'delivery_radius'
        )
        widgets = {
            'latitude': forms.NumberInput(attrs={'step': '0.000001'}),
            'longitude': forms.NumberInput(attrs={'step': '0.000001'}),
        }

class RestaurantHoursForm(forms.ModelForm):
    class Meta:
        model = RestaurantHours
        fields = ('day', 'opening_time', 'closing_time', 'is_closed')
        widgets = {
            'opening_time': forms.TimeInput(attrs={'type': 'time'}),
            'closing_time': forms.TimeInput(attrs={'type': 'time'}),
        }

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'description')

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = (
            'category', 'name', 'description', 'price', 'image',
            'is_available', 'preparation_time', 'is_vegetarian', 'is_vegan', 'is_featured'
        )

class MenuItemOptionForm(forms.ModelForm):
    class Meta:
        model = MenuItemOption
        fields = ('name',)

class MenuItemOptionChoiceForm(forms.ModelForm):
    class Meta:
        model = MenuItemOptionChoice
        fields = ('value', 'additional_price')