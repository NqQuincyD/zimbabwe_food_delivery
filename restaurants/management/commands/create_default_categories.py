from django.core.management.base import BaseCommand
from restaurants.models import Category

class Command(BaseCommand):
    help = 'Creates default food categories'

    def handle(self, *args, **kwargs):
        categories = [
            {
                'name': 'Appetizers',
                'description': 'Starters and small plates to begin your meal'
            },
            {
                'name': 'Main Courses',
                'description': 'Primary dishes and entrees'
            },
            {
                'name': 'Sides',
                'description': 'Accompaniments and side dishes'
            },
            {
                'name': 'Desserts',
                'description': 'Sweet treats and desserts'
            },
            {
                'name': 'Beverages',
                'description': 'Drinks and refreshments'
            },
            {
                'name': 'Traditional',
                'description': 'Local and traditional dishes'
            },
            {
                'name': 'Specials',
                'description': 'Chef\'s specials and featured items'
            },
        ]

        for category_data in categories:
            Category.objects.get_or_create(
                name=category_data['name'],
                defaults={'description': category_data['description']}
            )
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created category "{category_data["name"]}"')
            ) 