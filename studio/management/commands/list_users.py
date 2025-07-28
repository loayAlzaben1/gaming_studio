from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from studio.models import UserProfile
from django.utils import timezone

class Command(BaseCommand):
    help = 'List all users with their email addresses'

    def add_arguments(self, parser):
        parser.add_argument(
            '--gmail-only',
            action='store_true',
            help='Show only Gmail addresses'
        )
        parser.add_argument(
            '--active-only',
            action='store_true',
            help='Show only active users'
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=50,
            help='Limit number of results (default: 50)'
        )

    def handle(self, *args, **options):
        gmail_only = options['gmail_only']
        active_only = options['active_only']
        limit = options['limit']
        
        # Get users based on filters
        users = User.objects.all().select_related('profile').order_by('-date_joined')
        
        if gmail_only:
            users = users.filter(email__icontains='@gmail.com')
        
        if active_only:
            users = users.filter(is_active=True)
        
        users = users[:limit]
        
        # Display header
        self.stdout.write(
            self.style.SUCCESS(
                f'\n🎮 Gaming Studio Users {"(Gmail Only)" if gmail_only else ""} {"(Active Only)" if active_only else ""}'
            )
        )
        self.stdout.write('=' * 80)
        
        # Display users
        for i, user in enumerate(users, 1):
            try:
                profile = user.profile
                tier = profile.current_tier.name if profile.current_tier else 'None'
                donated = f'${profile.total_donated}'
            except UserProfile.DoesNotExist:
                tier = 'None'
                donated = '$0.00'
            
            status = '✅' if user.is_active else '❌'
            last_login = user.last_login.strftime('%Y-%m-%d') if user.last_login else 'Never'
            
            self.stdout.write(
                f'{i:2d}. {status} {user.username:<20} | {user.email:<35} | '
                f'Tier: {tier:<10} | Donated: {donated:<8} | Last: {last_login}'
            )
        
        # Display summary
        total_count = User.objects.count()
        gmail_count = User.objects.filter(email__icontains='@gmail.com').count()
        active_count = User.objects.filter(is_active=True).count()
        
        self.stdout.write('\n' + '=' * 80)
        self.stdout.write(f'📊 Total Users: {total_count} | Gmail: {gmail_count} | Active: {active_count}')
        self.stdout.write(f'Showing: {len(users)} users')
