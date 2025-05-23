from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),
    
    # Dashboard URLs
    path('dashboard/customer/', views.customer_dashboard, name='customer_dashboard'),
    path('dashboard/restaurant/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('dashboard/driver/', views.driver_dashboard, name='driver_dashboard'),
    
    # App URLs - Add the namespace
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('restaurants/', include('restaurants.urls', namespace='restaurants')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('delivery/', include('delivery.urls', namespace='delivery')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('reviews/', include('reviews.urls', namespace='reviews')),
    
    # Django allauth - this must be after accounts/ paths
    path('accounts/', include('allauth.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)