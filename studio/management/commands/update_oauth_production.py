from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Update Google OAuth settings for production'
    
    def handle(self, *args, **options):
        try:
            # Update or create the production site
            site, created = Site.objects.get_or_create(
                id=1,
                defaults={
                    'domain': 'gaming-studio.onrender.com',
                    'name': 'Gaming Studio Production'
                }
            )
            
            if not created:
                site.domain = 'gaming-studio.onrender.com'
                site.name = 'Gaming Studio Production'
                site.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Updated site: {site.domain}')
            )
            
            # Check if Google social app exists
            try:
                google_app = SocialApp.objects.get(provider='google')
                self.stdout.write(
                    self.style.SUCCESS(f'Google OAuth app found: {google_app.name}')
                )
                self.stdout.write(
                    self.style.WARNING('Please make sure these redirect URIs are configured in Google Cloud Console:')
                )
                self.stdout.write('- https://gaming-studio.onrender.com/accounts/google/login/callback/')
                self.stdout.write('- http://127.0.0.1:8000/accounts/google/login/callback/')
                self.stdout.write('- http://localhost:8000/accounts/google/login/callback/')
                
            except SocialApp.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR('Google OAuth app not found. Please create it in Django admin.')
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error updating OAuth settings: {e}')
            )
