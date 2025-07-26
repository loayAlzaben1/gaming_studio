from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Setup Google OAuth provider for production with real credentials'

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
                self.style.SUCCESS(f'✅ Updated site: {site.domain}')
            )
            
            # Create or update Google social app with production credentials
            google_app, created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Gaming Studio Google OAuth',
                    'client_id': '1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com',
                    'secret': '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',
                }
            )
            
            if not created:
                # Update existing app with new credentials
                google_app.name = 'Gaming Studio Google OAuth'
                google_app.client_id = '1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com'
                google_app.secret = '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'
                google_app.save()
            
            # Add site to the app
            google_app.sites.add(site)
            
            action = 'Created' if created else 'Updated'
            self.stdout.write(
                self.style.SUCCESS(f'✅ {action} Google OAuth app with production credentials')
            )
            self.stdout.write(
                self.style.SUCCESS('✅ Google OAuth is now configured for production!')
            )
            self.stdout.write(
                self.style.WARNING('🔒 Make sure these redirect URIs are configured in Google Cloud Console:')
            )
            self.stdout.write('   - https://gaming-studio.onrender.com/accounts/google/login/callback/')
            self.stdout.write('   - http://127.0.0.1:8000/accounts/google/login/callback/')
            self.stdout.write('   - http://localhost:8000/accounts/google/login/callback/')
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error setting up Google OAuth: {e}')
            )
