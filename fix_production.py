#!/usr/bin/env python
"""
Quick production fix script
Run this to fix production database and authentication issues
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaming_studio.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def main():
    print("🔧 Quick Production Fix for Gaming Studio")
    print("=" * 45)
    
    # 1. Run migrations
    print("🔄 Running migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed")
    except Exception as e:
        print(f"❌ Migration error: {e}")
    
    # 2. Setup site
    print("🌐 Setting up production site...")
    try:
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={'domain': 'gaming-studio.onrender.com', 'name': 'Gaming Studio'}
        )
        site.domain = 'gaming-studio.onrender.com'
        site.name = 'Gaming Studio'
        site.save()
        print(f"✅ Site configured: {site.domain}")
    except Exception as e:
        print(f"❌ Site setup error: {e}")
    
    # 3. Create Google OAuth app
    print("🔐 Setting up Google OAuth...")
    try:
        client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID', 'production-client-id')
        client_secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', 'production-client-secret')
        
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Google OAuth Production',
                'client_id': client_id,
                'secret': client_secret,
            }
        )
        
        if not created:
            google_app.client_id = client_id
            google_app.secret = client_secret
            google_app.save()
        
        google_app.sites.add(site)
        print("✅ Google OAuth configured")
    except Exception as e:
        print(f"❌ OAuth setup error: {e}")
    
    print("\n✅ Production fix completed!")
    print("🌐 Test authentication at: https://gaming-studio.onrender.com/accounts/login/")

if __name__ == "__main__":
    main()
