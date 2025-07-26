from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Setup Google OAuth with new credentials'
    
    def add_arguments(self, parser):
        parser.add_argument('--client-id', type=str, help='Google OAuth Client ID')
        parser.add_argument('--client-secret', type=str, help='Google OAuth Client Secret')
    
    def handle(self, *args, **options):
        client_id = options.get('client_id')
        client_secret = options.get('client_secret')
        
        if not client_id or not client_secret:
            self.stdout.write(
                self.style.ERROR('Please provide both --client-id and --client-secret')
            )
            self.stdout.write('Usage: python manage.py setup_new_google_oauth --client-id YOUR_CLIENT_ID --client-secret YOUR_CLIENT_SECRET')
            return
        
        try:
            # Ensure site exists
            site, created = Site.objects.get_or_create(
                id=1,
                defaults={
                    'domain': 'gaming-studio.onrender.com',
                    'name': 'Gaming Studio'
                }
            )
            
            # Create or update Google social app
            google_app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Google',
                    'client_id': client_id,
                    'secret': client_secret,
                }
            )
            
            if not created:
                google_app.client_id = client_id
                google_app.secret = client_secret
                google_app.save()
            
            # Associate with site
            google_app.sites.add(site)
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(
                self.style.SUCCESS(f'{action} Google OAuth app successfully!')
            )
            self.stdout.write(f'Client ID: {client_id[:20]}...')
            self.stdout.write(f'Site: {site.domain}')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error setting up Google OAuth: {e}')
            )
