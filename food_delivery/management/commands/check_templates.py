# Create file: food_delivery/management/commands/check_templates.py

from django.core.management.base import BaseCommand
from django.urls import URLResolver, URLPattern
from django.urls import get_resolver
from django.http import HttpRequest
from django.template.response import TemplateResponse
from django.template.exceptions import TemplateDoesNotExist

class Command(BaseCommand):
    help = 'Check that all views render templates properly'
    
    def handle(self, *args, **options):
        resolver = get_resolver()
        self.check_urls(resolver.url_patterns)
    
    def check_urls(self, url_patterns, namespace=None, prefix=''):
        for pattern in url_patterns:
            if isinstance(pattern, URLResolver):
                ns = pattern.namespace if pattern.namespace else namespace
                prefix = pattern.pattern.regex.pattern if hasattr(pattern.pattern, 'regex') else pattern.pattern._regex
                self.check_urls(pattern.url_patterns, namespace=ns, prefix=prefix)
            elif isinstance(pattern, URLPattern):
                view_name = pattern.name
                if view_name:
                    full_name = ':'.join(filter(None, [namespace, view_name]))
                    self.stdout.write(f"Checking view: {full_name}")