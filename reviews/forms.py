from django import forms
from .models import RestaurantReview, MenuItemReview, DriverReview

class RestaurantReviewForm(forms.ModelForm):
    class Meta:
        model = RestaurantReview
        fields = ('rating', 'food_rating', 'service_rating', 'comment')
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

class MenuItemReviewForm(forms.ModelForm):
    class Meta:
        model = MenuItemReview
        fields = ('rating', 'comment')
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

class DriverReviewForm(forms.ModelForm):
    class Meta:
        model = DriverReview
        fields = ('rating', 'comment')
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3}),
        }