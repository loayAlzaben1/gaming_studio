#!/usr/bin/env python
"""
Emergency production database fix
This script directly creates all necessary tables and configurations
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaming_studio.settings')
django.setup()

from django.db import connection
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from django.contrib.auth.models import User

def create_tables_directly():
    """Create tables directly via SQL if migrations fail"""
    print("🔧 Creating tables directly...")
    
    with connection.cursor() as cursor:
        # Create studio_game table
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS studio_game (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            description TEXT,
            cover_image VARCHAR(100),
            is_featured BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Create account_emailaddress table for allauth
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS account_emailaddress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            email VARCHAR(254) NOT NULL,
            verified BOOLEAN DEFAULT 0,
            primary_key BOOLEAN DEFAULT 0,
            FOREIGN KEY (user_id) REFERENCES auth_user (id)
        );
        """)
        
        # Create socialaccount tables
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS socialaccount_socialapp (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            provider VARCHAR(30) NOT NULL,
            name VARCHAR(40) NOT NULL,
            client_id VARCHAR(191) NOT NULL,
            secret VARCHAR(191) NOT NULL,
            key VARCHAR(191) DEFAULT ''
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS socialaccount_socialapp_sites (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            socialapp_id INTEGER NOT NULL,
            site_id INTEGER NOT NULL,
            FOREIGN KEY (socialapp_id) REFERENCES socialaccount_socialapp (id),
            FOREIGN KEY (site_id) REFERENCES django_site (id)
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS socialaccount_socialaccount (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            provider VARCHAR(30) NOT NULL,
            uid VARCHAR(191) NOT NULL,
            last_login DATETIME,
            date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
            extra_data TEXT DEFAULT '{}',
            FOREIGN KEY (user_id) REFERENCES auth_user (id)
        );
        """)
        
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS socialaccount_socialtoken (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            app_id INTEGER NOT NULL,
            account_id INTEGER NOT NULL,
            token TEXT NOT NULL,
            token_secret TEXT DEFAULT '',
            expires_at DATETIME,
            FOREIGN KEY (app_id) REFERENCES socialaccount_socialapp (id),
            FOREIGN KEY (account_id) REFERENCES socialaccount_socialaccount (id)
        );
        """)
        
        print("✅ Core tables created")

def setup_site_and_oauth():
    """Setup site and OAuth configuration"""
    print("🌐 Setting up site and OAuth...")
    
    # Setup site
    site, created = Site.objects.get_or_create(
        pk=1,
        defaults={
            'domain': 'gaming-studio.onrender.com',
            'name': 'Gaming Studio'
        }
    )
    site.domain = 'gaming-studio.onrender.com'
    site.name = 'Gaming Studio'
    site.save()
    print(f"✅ Site configured: {site.domain}")
    
    # Setup Google OAuth
    client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID', '1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com')
    client_secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', 'GOCSPX-your-secret-here')
    
    google_app, created = SocialApp.objects.get_or_create(
        provider='google',
        defaults={
            'name': 'Gaming Studio Google OAuth',
            'client_id': client_id,
            'secret': client_secret,
        }
    )
    
    if not created:
        google_app.name = 'Gaming Studio Google OAuth'
        google_app.client_id = client_id
        google_app.secret = client_secret
        google_app.save()
    
    google_app.sites.add(site)
    print("✅ Google OAuth configured")

def create_sample_data():
    """Create sample game if none exists"""
    from studio.models import Game
    
    if Game.objects.count() == 0:
        Game.objects.create(
            title="RTS Strategy Game",
            description="An epic real-time strategy game with immersive gameplay.",
            is_featured=True
        )
        print("✅ Sample game created")
    else:
        print("✅ Games already exist")

def main():
    print("🚨 EMERGENCY PRODUCTION FIX - Gaming Studio")
    print("=" * 50)
    
    try:
        # Step 1: Create tables directly
        create_tables_directly()
        
        # Step 2: Setup site and OAuth
        setup_site_and_oauth()
        
        # Step 3: Create sample data
        create_sample_data()
        
        # Step 4: Verify everything works
        print("🔍 Verifying setup...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='studio_game';")
            game_table = bool(cursor.fetchone())
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='account_emailaddress';")
            auth_table = bool(cursor.fetchone())
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='socialaccount_socialapp';")
            oauth_table = bool(cursor.fetchone())
        
        if game_table and auth_table and oauth_table:
            print("✅ ALL TABLES CREATED SUCCESSFULLY!")
            print("🌐 Production site should now work:")
            print("   - https://gaming-studio.onrender.com/accounts/login/")
            print("   - https://gaming-studio.onrender.com/accounts/signup/")
            print("   - https://gaming-studio.onrender.com/games/")
            return 0
        else:
            print(f"❌ Some tables missing: game={game_table}, auth={auth_table}, oauth={oauth_table}")
            return 1
            
    except Exception as e:
        print(f"❌ Emergency fix failed: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
