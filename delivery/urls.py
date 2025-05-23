from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('available-orders/', views.available_orders, name='available_orders'),
    path('request/<int:order_id>/', views.request_delivery, name='request_delivery'),
    path('accept-request/<int:request_id>/', views.accept_delivery_request, name='accept_delivery_request'),
    path('decline-request/<int:request_id>/', views.decline_delivery_request, name='decline_delivery_request'),
    path('rate/<int:order_id>/', views.rate_delivery, name='rate_delivery'),
    path('update-location/', views.update_driver_location, name='update_driver_location'),
]