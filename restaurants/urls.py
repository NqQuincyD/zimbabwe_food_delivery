from django.urls import path
from . import views

app_name = 'restaurants'

urlpatterns = [
    path('', views.RestaurantListView.as_view(), name='restaurant_list'),
    path('create/', views.RestaurantCreateView.as_view(), name='restaurant_create'),
    path('<slug:slug>/', views.RestaurantDetailView.as_view(), name='restaurant_detail'),
    path('<int:pk>/edit/', views.RestaurantUpdateView.as_view(), name='restaurant_update'),
    path('<int:pk>/manage/', views.RestaurantManageView.as_view(), name='restaurant_manage'),
    path('<int:pk>/toggle-status/', views.toggle_status, name='toggle_status'),
    
    # Menu management
    path('<int:restaurant_id>/menu/add/', views.MenuItemCreateView.as_view(), name='menuitem_create'),
    path('menu/<int:pk>/edit/', views.MenuItemUpdateView.as_view(), name='menuitem_update'),
    path('menu/<int:pk>/delete/', views.MenuItemDeleteView.as_view(), name='menuitem_delete'),
    
    # Hours management
    path('<int:restaurant_id>/hours/add/', views.RestaurantHoursCreateView.as_view(), name='restaurant_hours_create'),
    path('hours/<int:pk>/edit/', views.RestaurantHoursUpdateView.as_view(), name='restaurant_hours_update'),
]