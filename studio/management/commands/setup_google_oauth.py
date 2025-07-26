from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Setup Google OAuth provider for development'

    def handle(self, *args, **options):
        # Get or create the default site
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
                'name': 'Google OAuth (Development)',
                'client_id': 'dummy-client-id-for-development',
                'secret': 'dummy-secret-for-development',
            }
        )
        
        # Add site to the app
        google_app.sites.add(site)
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully created Google OAuth app for development.\n'
                    'Note: This uses dummy credentials. For production, you need to:\n'
                    '1. Create a Google Cloud Console project\n'
                    '2. Enable Google+ API\n'
                    '3. Create OAuth 2.0 credentials\n'
                    '4. Update the SocialApp in Django admin with real credentials'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING('Google OAuth app already exists.')
            )
