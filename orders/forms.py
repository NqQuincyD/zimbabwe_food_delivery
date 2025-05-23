from django import forms
from .models import Order, OrderItem, OrderItemOptionChoice

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('delivery_address', 'delivery_instructions')

class OrderItemForm(forms.Form):
    menu_item_id = forms.IntegerField(widget=forms.HiddenInput())
    quantity = forms.IntegerField(min_value=1, initial=1)
    special_instructions = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}))
    
class OrderStatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('status',)