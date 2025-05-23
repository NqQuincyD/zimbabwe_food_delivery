from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    
    # Address management
    path('addresses/', views.AddressListView.as_view(), name='address_list'),
    path('addresses/add/', views.AddressCreateView.as_view(), name='address_create'),
    path('addresses/<int:pk>/edit/', views.AddressUpdateView.as_view(), name='address_update'),
    path('addresses/<int:pk>/delete/', views.AddressDeleteView.as_view(), name='address_delete'),
    
    # Driver specific
    path('driver/toggle-availability/', views.driver_toggle_availability, name='driver_toggle_availability'),
    path('driver/dashboard/', views.DriverDashboardView.as_view(), name='driver_dashboard'),
]