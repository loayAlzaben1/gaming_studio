from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
import os


class Command(BaseCommand):
    help = 'Setup Google OAuth provider for production and development'

    def add_arguments(self, parser):
        parser.add_argument(
            '--production',
            action='store_true',
            help='Setup for production environment',
        )

    def handle(self, *args, **options):
        if options['production']:
            # Production setup
            site, created = Site.objects.get_or_create(
                pk=1,
                defaults={
                    'domain': 'gaming-studio.onrender.com',
                    'name': 'Gaming Studio'
                }
            )
            
            # Update site for production
            site.domain = 'gaming-studio.onrender.com'
            site.name = 'Gaming Studio'
            site.save()
            
            # Get production OAuth credentials from environment
            client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID', 'your-production-client-id')
            client_secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', 'your-production-client-secret')
            
            google_app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Google OAuth Production',
                    'client_id': client_id,
                    'secret': client_secret,
                }
            )
            
            if not created:
                google_app.name = 'Google OAuth Production'
                google_app.client_id = client_id
                google_app.secret = client_secret
                google_app.save()
            
            self.stdout.write(f'✓ Production site configured: {site.domain}')
        else:
            # Development setup
            site, created = Site.objects.get_or_create(
                pk=1,
                defaults={  
                    'domain': '127.0.0.1:8000',
                    'name': 'Gaming Studio Development'
                }
            )

            # Create Google social app for development (with dummy credentials)
            google_app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Google OAuth Development',
                    'client_id': 'development-client-id',
                    'secret': 'development-client-secret',
                }
            )
            
            self.stdout.write(f'✓ Development site configured: {site.domain}')

        # Add site to Google app
        google_app.sites.add(site)
        
        action = 'Created' if created else 'Updated'
        self.stdout.write(
            self.style.SUCCESS(
                f'{action} Google OAuth app: {google_app.name}\n'
                f'Client ID: {google_app.client_id}\n'
                f'Site: {site.domain}'
            )
        )
