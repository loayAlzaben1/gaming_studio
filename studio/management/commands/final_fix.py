from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp
from studio.models import Game
import os

class Command(BaseCommand):
    help = 'Final production fix - add missing data and OAuth'

    def handle(self, *args, **options):
        self.stdout.write("🔧 FINAL PRODUCTION FIX")
        
        # 1. Create sample game if missing
        if Game.objects.count() == 0:
            game = Game.objects.create(
                title="RTS Strategy Game",
                description="An epic real-time strategy game with immersive gameplay and stunning graphics.",
                is_featured=True
            )
            self.stdout.write(f"✅ Created sample game: {game.title}")
        else:
            self.stdout.write("✅ Games already exist")
        
        # 2. Setup production site
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={'domain': 'gaming-studio.onrender.com', 'name': 'Gaming Studio'}
        )
        site.domain = 'gaming-studio.onrender.com'
        site.name = 'Gaming Studio'
        site.save()
        self.stdout.write(f"✅ Site configured: {site.domain}")
        
        # 3. Setup Google OAuth
        client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID', '1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com')
        client_secret = os.environ.get('GOOGLE_OAUTH_CLIENT_SECRET', 'GOCSPX-production-secret-here')
        
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
        
        action = "Created" if created else "Updated"
        self.stdout.write(f"✅ {action} Google OAuth app")
        
        # 4. Verify everything
        game_count = Game.objects.count()
        oauth_apps = SocialApp.objects.filter(provider='google').count()
        
        self.stdout.write(self.style.SUCCESS(
            f"🎉 FINAL FIX COMPLETE!\n"
            f"   Games: {game_count}\n"
            f"   OAuth apps: {oauth_apps}\n"
            f"   Site: {site.domain}\n"
            f"   ✅ Authentication should work now!"
        ))
