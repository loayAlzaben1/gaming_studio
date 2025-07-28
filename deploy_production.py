#!/usr/bin/env python
"""
Production deployment script for Gaming Studio
Handles database setup, migrations, and OAuth configuration
"""
import os
import sys
import django

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaming_studio.settings')
django.setup()

from django.core.management import execute_from_command_line
from django.db import connection
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from studio.models import Game

def check_database():
    """Check database connection and tables"""
    print("🔍 Checking database connection...")
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Database connection OK")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def run_migrations():
    """Run all Django migrations"""
    print("🔄 Running database migrations...")
    try:
        execute_from_command_line(['manage.py', 'migrate', '--verbosity=2'])
        print("✅ Migrations completed")
        return True
    except Exception as e:
        print(f"❌ Migrations failed: {e}")
        return False

def setup_production_site():
    """Setup production site configuration"""
    print("🌐 Setting up production site...")
    try:
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
        
        action = "Created" if created else "Updated"
        print(f"✅ {action} production site: {site.domain}")
        return True
    except Exception as e:
        print(f"❌ Site setup failed: {e}")
        return False

def setup_google_oauth():
    """Setup Google OAuth for production"""
    print("🔐 Setting up Google OAuth...")
    try:
        # Get OAuth credentials from environment
        client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
        client_secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET')
        
        if not client_id or not client_secret:
            print("⚠️ Google OAuth credentials not found in environment variables")
            print("   Set GOOGLE_OAUTH_CLIENT_ID and GOOGLE_OAUTH_CLIENT_SECRET")
            return False
        
        # Get production site
        site = Site.objects.get(pk=1)
        
        # Create or update Google OAuth app
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
        
        # Associate with site
        google_app.sites.add(site)
        
        action = "Created" if created else "Updated"
        print(f"✅ {action} Google OAuth app for production")
        return True
    except Exception as e:
        print(f"❌ Google OAuth setup failed: {e}")
        return False

def create_sample_data():
    """Create sample game data if none exists"""
    print("🎮 Checking for sample data...")
    try:
        if Game.objects.count() == 0:
            print("📦 Creating sample game data...")
            Game.objects.create(
                title="RTS Strategy Game",
                description="An epic real-time strategy game with immersive gameplay and stunning graphics.",
                is_featured=True
            )
            print("✅ Sample game created")
        else:
            print("✅ Game data already exists")
        return True
    except Exception as e:
        print(f"❌ Sample data creation failed: {e}")
        return False

def main():
    """Main deployment script"""
    print("🚀 Starting Gaming Studio Production Deployment")
    print("=" * 50)
    
    steps = [
        ("Database Connection", check_database),
        ("Migrations", run_migrations),
        ("Production Site", setup_production_site),
        ("Google OAuth", setup_google_oauth),
        ("Sample Data", create_sample_data),
    ]
    
    success_count = 0
    for step_name, step_func in steps:
        print(f"\n📋 Step: {step_name}")
        if step_func():
            success_count += 1
        else:
            print(f"⚠️ {step_name} had issues but continuing...")
    
    print("\n" + "=" * 50)
    print(f"🎯 Deployment Summary: {success_count}/{len(steps)} steps completed")
    
    if success_count >= 3:  # At least database, migrations, and site setup
        print("✅ Deployment successful! Gaming Studio is ready.")
        print("🌐 Visit: https://gaming-studio.onrender.com")
        print("🔐 Login: https://gaming-studio.onrender.com/accounts/login/")
    else:
        print("❌ Deployment had critical issues. Check the logs above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
