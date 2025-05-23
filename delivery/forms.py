from django import forms
from .models import DeliveryZone, DeliveryRequest, DeliveryRating

class DeliveryZoneForm(forms.ModelForm):
    class Meta:
        model = DeliveryZone
        fields = ('name', 'description', 'base_fee')

class DeliveryRequestResponseForm(forms.ModelForm):
    class Meta:
        model = DeliveryRequest
        fields = ('status',)

class DeliveryRatingForm(forms.ModelForm):
    class Meta:
        model = DeliveryRating
        fields = ('rating', 'comment')