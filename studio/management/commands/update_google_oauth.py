from django.core.management.base import BaseCommand
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from django.conf import settings


class Command(BaseCommand):
    help = 'Update Google OAuth credentials for current environment'

    def add_arguments(self, parser):
        parser.add_argument('--client-id', type=str, help='Google OAuth Client ID')
        parser.add_argument('--client-secret', type=str, help='Google OAuth Client Secret')
        parser.add_argument('--production', action='store_true', help='Configure for production')

    def handle(self, *args, **options):
        client_id = options.get('client_id')
        client_secret = options.get('client_secret')
        is_production = options.get('production', False)

        # Determine environment-specific settings
        if is_production or 'gaming-studio.onrender.com' in settings.ALLOWED_HOSTS:
            domain = 'gaming-studio.onrender.com'
            name = 'Gaming Studio Production'
            # Use provided credentials or existing production ones
            default_client_id = client_id or '49621374950-b7knjfh86kkn2norpblsgsjk87sg632n.apps.googleusercontent.com'
            default_client_secret = client_secret or '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'
        else:
            domain = '127.0.0.1:8000'
            name = 'Gaming Studio Development'
            # Use provided credentials or existing development ones
            default_client_id = client_id or '49621374950-b7knjfh86kkn2norpblsgsjk87sg632n.apps.googleusercontent.com'
            default_client_secret = client_secret or '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'

        try:
            # Get or create the site
            site, created = Site.objects.get_or_create(
                pk=1,
                defaults={'domain': domain, 'name': name}
            )
            
            if not created:
                site.domain = domain
                site.name = name
                site.save()

            # Get or create Google social app
            google_app, app_created = SocialApp.objects.get_or_create(
                provider='google',
                defaults={
                    'name': 'Gaming Studio Google OAuth',
                    'client_id': default_client_id,
                    'secret': default_client_secret,
                }
            )

            if not app_created:
                google_app.client_id = default_client_id
                google_app.secret = default_client_secret
                google_app.name = 'Gaming Studio Google OAuth'
                google_app.save()

            # Associate with site
            google_app.sites.clear()
            google_app.sites.add(site)

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully configured Google OAuth for {name}!\n'
                    f'  Site: {site.domain}\n'
                    f'  Client ID: {google_app.client_id}\n'
                    f'  Environment: {"Production" if is_production else "Development"}\n'
                    '\nMake sure your Google Cloud Console has these redirect URIs:\n'
                    f'  https://{domain}/accounts/google/login/callback/\n'
                    '  http://127.0.0.1:8000/accounts/google/login/callback/'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error configuring OAuth credentials: {e}')
            )
