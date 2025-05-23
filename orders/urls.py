from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('cart/', views.CartView.as_view(), name='cart'),
    path('add-to-cart/<int:menu_item_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<str:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('clear-cart/', views.clear_cart, name='clear_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('list/', views.OrderListView.as_view(), name='order_list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order_detail'),
    path('<int:pk>/update-status/', views.update_order_status, name='update_order_status'),
]