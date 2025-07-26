from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site


class Command(BaseCommand):
    help = 'Update Google OAuth credentials with real values'

    def handle(self, *args, **options):
        # Get or create the default site
        site, created = Site.objects.get_or_create(
            pk=1,
            defaults={
                'domain': '127.0.0.1:8000',
                'name': 'Gaming Studio Development'
            }
        )
        
        # Update Google social app with real credentials
        try:
            google_app = SocialApp.objects.get(provider='google')
            google_app.name = 'Gaming Studio Google OAuth'
            google_app.client_id = '49621374950-b7knjfh86kkn2norpblsgsjk87sg632n.apps.googleusercontent.com'
            google_app.secret = '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'
            google_app.save()
            
            # Make sure site is associated
            google_app.sites.add(site)
            
            self.stdout.write(
                self.style.SUCCESS(
                    'Successfully updated Google OAuth credentials!\n'
                    f'Client ID: {google_app.client_id}\n'
                    'Your Google OAuth is now ready to use!'
                )
            )
        except SocialApp.DoesNotExist:
            self.stdout.write(
                self.style.ERROR('Google OAuth app not found. Run setup_google_oauth first.')
            )
