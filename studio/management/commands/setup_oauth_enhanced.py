"""
Enhanced OAuth configuration with additional debugging
"""
from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os

class Command(BaseCommand):
    help = 'Enhanced Google OAuth setup with debugging'

    def handle(self, *args, **options):
        self.stdout.write("🔐 ENHANCED GOOGLE OAUTH SETUP...")
        
        # 1. Setup production site with additional domains
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={'domain': 'gaming-studio.onrender.com', 'name': 'Gaming Studio Production'}
        )
        site.domain = 'gaming-studio.onrender.com'
        site.name = 'Gaming Studio Production'
        site.save()
        self.stdout.write(f"✅ Primary Site: {site.domain}")
        
        # 2. Setup Google OAuth app with enhanced configuration
        client_secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', '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')
        
        # Delete any existing Google apps to start fresh
        SocialApp.objects.filter(provider='google').delete()
        
        google_app = SocialApp.objects.create(
            provider='google',
            name='Gaming Studio Google OAuth Enhanced',
            client_id='1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com',
            secret=client_secret,
        )
        
        # 3. Associate with site
        google_app.sites.add(site)
        
        self.stdout.write(self.style.SUCCESS("✅ Enhanced Google OAuth configured!"))
        self.stdout.write(f"   Client ID: {google_app.client_id}")
        self.stdout.write(f"   App Name: {google_app.name}")
        self.stdout.write(f"   Sites: {[s.domain for s in google_app.sites.all()]}")
        
        # 4. Display required redirect URIs for Google Console
        self.stdout.write(self.style.WARNING("\n📋 REQUIRED REDIRECT URIs for Google Console:"))
        redirect_uris = [
            "https://gaming-studio.onrender.com/accounts/google/login/callback/",
            "http://127.0.0.1:8000/accounts/google/login/callback/",
            "http://localhost:8000/accounts/google/login/callback/",
            "https://gaming-studio.onrender.com/accounts/google/login/",
            "https://gaming-studio.onrender.com/accounts/social/login/cancelled/",
        ]
        
        for i, uri in enumerate(redirect_uris, 1):
            self.stdout.write(f"   URI {i}: {uri}")
            
        self.stdout.write("\n🎉 Enhanced OAuth setup complete!")
        self.stdout.write("🔧 If you get 403 errors, make sure ALL URIs above are in Google Console!")
