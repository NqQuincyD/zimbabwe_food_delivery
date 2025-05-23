from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy, reverse
from django.contrib import messages
from django.db.models import Avg, Count, Q
from .models import Restaurant, Category, MenuItem, RestaurantHours
from .forms import (
    RestaurantForm, CategoryForm, MenuItemForm, 
    MenuItemOptionForm, MenuItemOptionChoiceForm, RestaurantHoursForm
)
from reviews.models import RestaurantReview
from django.utils import timezone
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required

class RestaurantListView(ListView):
    model = Restaurant
    template_name = 'restaurants/restaurant_list.html'
    context_object_name = 'restaurants'
    paginate_by = 12
    
    def get_queryset(self):
        queryset = Restaurant.objects.filter(is_approved=True)
        
        # Search by name or description
        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        
        # Filter by city
        city = self.request.GET.get('city')
        if city:
            queryset = queryset.filter(city__iexact=city)
        
        # Sort results
        sort_by = self.request.GET.get('sort', 'rating')
        if sort_by == 'rating':
            queryset = queryset.order_by('-average_rating')
        elif sort_by == 'name':
            queryset = queryset.order_by('name')
        
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['cities'] = Restaurant.objects.filter(is_approved=True).values_list('city', flat=True).distinct()
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_city'] = self.request.GET.get('city', '')
        context['sort_by'] = self.request.GET.get('sort', 'rating')
        return context

class RestaurantDetailView(DetailView):
    model = Restaurant
    template_name = 'restaurants/restaurant_detail.html'
    context_object_name = 'restaurant'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = self.get_object()
        
        # Get menu items grouped by category
        menu_by_category = {}
        categories = Category.objects.all()
        for category in categories:
            items = MenuItem.objects.filter(restaurant=restaurant, category=category, is_available=True)
            if items.exists():
                menu_by_category[category] = items
        
        context['menu_by_category'] = menu_by_category
        context['hours'] = restaurant.hours.all().order_by('day')
        
        # Get reviews
        context['reviews'] = RestaurantReview.objects.filter(restaurant=restaurant).order_by('-created_at')[:5]
        context['review_count'] = RestaurantReview.objects.filter(restaurant=restaurant).count()
        
        return context

class RestaurantCreateView(LoginRequiredMixin, CreateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = 'restaurants/restaurant_form.html'
    
    def form_valid(self, form):
        form.instance.owner = self.request.user
        response = super().form_valid(form)
        messages.success(self.request, 'Restaurant created successfully. It will be reviewed for approval.')
        return response
    
    def get_success_url(self):
        return reverse('restaurants:restaurant_manage', kwargs={'pk': self.object.pk})

class RestaurantUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Restaurant
    form_class = RestaurantForm
    template_name = 'restaurants/restaurant_form.html'
    
    def test_func(self):
        restaurant = self.get_object()
        return self.request.user == restaurant.owner
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Restaurant information updated successfully.')
        return response
    
    def get_success_url(self):
        return reverse('restaurants:restaurant_manage', kwargs={'pk': self.object.pk})

class RestaurantManageView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
    model = Restaurant
    template_name = 'restaurants/restaurant_manage.html'
    context_object_name = 'restaurant'
    
    def test_func(self):
        restaurant = self.get_object()
        return self.request.user == restaurant.owner
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        restaurant = self.get_object()
        
        context['menu_items'] = MenuItem.objects.filter(restaurant=restaurant).order_by('category', 'name')
        context['hours'] = RestaurantHours.objects.filter(restaurant=restaurant).order_by('day')
        context['pending_orders'] = restaurant.orders.filter(status__in=['PENDING', 'ACCEPTED', 'PREPARING']).order_by('-ordered_at')
        context['today_orders'] = restaurant.orders.filter(ordered_at__date=timezone.now().date())
        
        return context

class MenuItemCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'restaurants/menuitem_form.html'
    
    def test_func(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        return self.request.user == restaurant.owner
    
    def form_valid(self, form):
        restaurant_id = self.kwargs.get('restaurant_id')
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        form.instance.restaurant = restaurant
        response = super().form_valid(form)
        messages.success(self.request, 'Menu item added successfully.')
        return response
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurant_id'] = self.kwargs.get('restaurant_id')
        return context
    
    def get_success_url(self):
        return reverse('restaurants:restaurant_manage', kwargs={'pk': self.kwargs.get('restaurant_id')})

class MenuItemUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = MenuItem
    form_class = MenuItemForm
    template_name = 'restaurants/menuitem_form.html'
    
    def test_func(self):
        menu_item = self.get_object()
        return self.request.user == menu_item.restaurant.owner
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Menu item updated successfully.')
        return response
    
    def get_success_url(self):
        return reverse('restaurants:restaurant_manage', kwargs={'pk': self.object.restaurant.id})

class MenuItemDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = MenuItem
    template_name = 'restaurants/menuitem_confirm_delete.html'
    
    def test_func(self):
        menu_item = self.get_object()
        return self.request.user == menu_item.restaurant.owner
    
    def get_success_url(self):
        return reverse('restaurants:restaurant_manage', kwargs={'pk': self.object.restaurant.id})
    
    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Menu item deleted successfully.')
        return super().delete(request, *args, **kwargs)

class RestaurantHoursCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = RestaurantHours
    form_class = RestaurantHoursForm
    template_name = 'restaurants/restaurant_hours_form.html'
    
    def test_func(self):
        restaurant_id = self.kwargs.get('restaurant_id')
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        return self.request.user == restaurant.owner
    
    def form_valid(self, form):
        restaurant_id = self.kwargs.get('restaurant_id')
        restaurant = get_object_or_404(Restaurant, id=restaurant_id)
        form.instance.restaurant = restaurant
        
        # Check if hours already exist for this day
        day = form.cleaned_data.get('day')
        existing_hours = RestaurantHours.objects.filter(restaurant=restaurant, day=day)
        if existing_hours.exists():
            form.add_error('day', 'Hours for this day already exist. Please update the existing entry.')
            return self.form_invalid(form)
        
        response = super().form_valid(form)
        messages.success(self.request, 'Restaurant hours added successfully.')
        return response
    
    def get_success_url(self):
        return reverse('restaurants:restaurant_manage', kwargs={'pk': self.kwargs.get('restaurant_id')})

class RestaurantHoursUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = RestaurantHours
    form_class = RestaurantHoursForm
    template_name = 'restaurants/restaurant_hours_form.html'
    
    def test_func(self):
        hours = self.get_object()
        return self.request.user == hours.restaurant.owner
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Restaurant hours updated successfully.')
        return response
    
    def get_success_url(self):
        return reverse('restaurants:restaurant_manage', kwargs={'pk': self.object.restaurant.id})

@login_required
@require_POST
def toggle_status(request, pk):
    restaurant = get_object_or_404(Restaurant, pk=pk)
    if request.user != restaurant.owner:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    restaurant.is_open = not restaurant.is_open
    restaurant.save()
    
    return JsonResponse({
        'status': 'success',
        'is_open': restaurant.is_open,
        'message': f'Restaurant is now {"open" if restaurant.is_open else "closed"}'
    })