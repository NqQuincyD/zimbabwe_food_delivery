from django.urls import path
from . import views

app_name = 'reviews'

urlpatterns = [
    path('restaurant/<int:restaurant_id>/', views.restaurant_review, name='restaurant_review'),
    path('menu-item/<int:item_id>/', views.menu_item_review, name='menu_item_review'),
    path('driver/<int:order_id>/', views.driver_review, name='driver_review'),
]