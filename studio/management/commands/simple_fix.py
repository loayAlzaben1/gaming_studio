from django.core.management.base import BaseCommand
from django.db import connection
from django.contrib.sites.models import Site

class Command(BaseCommand):
    help = 'Super simple production fix'

    def handle(self, *args, **options):
        self.stdout.write("🚨 SUPER SIMPLE FIX")
        
        # Create studio_game table
        with connection.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS studio_game (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL DEFAULT 'Sample Game',
                description TEXT DEFAULT 'A sample game',
                cover_image TEXT DEFAULT '',
                is_featured INTEGER DEFAULT 1,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            );
            """)
            
            cursor.execute("SELECT COUNT(*) FROM studio_game;")
            if cursor.fetchone()[0] == 0:
                cursor.execute("""
                INSERT INTO studio_game (title, description, is_featured) 
                VALUES ('RTS Strategy Game', 'Epic gaming experience', 1);
                """)
        
        # Setup site
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={'domain': 'gaming-studio.onrender.com', 'name': 'Gaming Studio'}
        )
        site.domain = 'gaming-studio.onrender.com'
        site.save()
        
        # Setup OAuth if possible
        try:
            from allauth.socialaccount.models import SocialApp
            google_app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Gaming Studio Google OAuth',
                    'client_id': '1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com',
                    'secret': 'production-secret',
                }
            )
            google_app.sites.add(site)
        except:
            pass
        
        self.stdout.write(self.style.SUCCESS("✅ Simple fix completed!"))
