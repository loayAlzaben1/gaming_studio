from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os

class Command(BaseCommand):
    help = 'Set up Google OAuth immediately'

    def handle(self, *args, **options):
        self.stdout.write("🔐 SETTING UP GOOGLE OAUTH...")
        
        # 1. Setup production site
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={'domain': 'gaming-studio.onrender.com', 'name': 'Gaming Studio'}
        )
        site.domain = 'gaming-studio.onrender.com'
        site.name = 'Gaming Studio'
        site.save()
        self.stdout.write(f"✅ Site: {site.domain}")
        
        # 2. Setup Google OAuth app with your existing credentials
        # Use the new client secret from July 29, 2025
        client_secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', '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')
        
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Gaming Studio Google OAuth',
                'client_id': '1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com',
                'secret': client_secret,
            }
        )
        
        if not created:
            google_app.name = 'Gaming Studio Google OAuth'
            google_app.client_id = '1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com'
            google_app.secret = client_secret
            google_app.save()
        
        # 3. Associate with site
        google_app.sites.add(site)
        
        self.stdout.write(self.style.SUCCESS("✅ Google OAuth configured!"))
        self.stdout.write(f"   Client ID: {google_app.client_id}")
        self.stdout.write("🎉 Gmail sign-in should work now!")
