from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
import os

class Command(BaseCommand):
    help = 'Emergency fix for production database tables'

    def handle(self, *args, **options):
        self.stdout.write("🚨 EMERGENCY DATABASE FIX")
        self.stdout.write("=" * 40)
        
        # Create tables directly
        self.stdout.write("🔧 Creating missing tables...")
        with connection.cursor() as cursor:
            # Studio game table
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
            
            # Essential auth tables
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS account_emailaddress (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                email VARCHAR(254) NOT NULL,
                verified BOOLEAN DEFAULT 0,
                primary_key BOOLEAN DEFAULT 0
            );
            """)
            
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
                site_id INTEGER NOT NULL
            );
            """)
        
        self.stdout.write(self.style.SUCCESS("✅ Tables created"))
        
        # Setup site
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={'domain': 'gaming-studio.onrender.com', 'name': 'Gaming Studio'}
        )
        site.domain = 'gaming-studio.onrender.com'
        site.save()
        self.stdout.write(f"✅ Site: {site.domain}")
        
        # Setup OAuth
        google_app, created = SocialApp.objects.get_or_create(
            provider='google',
            defaults={
                'name': 'Gaming Studio Google OAuth',
                'client_id': os.environ.get('GOOGLE_OAUTH_CLIENT_ID', '1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com'),
                'secret': os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', 'production-secret'),
            }
        )
        google_app.sites.add(site)
        self.stdout.write("✅ OAuth configured")
        
        # Create sample game
        from studio.models import Game
        if Game.objects.count() == 0:
            Game.objects.create(
                title="RTS Strategy Game",
                description="Epic real-time strategy gaming experience",
                is_featured=True
            )
            self.stdout.write("✅ Sample game created")
        
        self.stdout.write(self.style.SUCCESS("🎉 EMERGENCY FIX COMPLETED!"))
        self.stdout.write("Test: https://gaming-studio.onrender.com/accounts/login/")
