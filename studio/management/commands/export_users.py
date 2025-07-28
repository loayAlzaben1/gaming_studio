from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from studio.models import UserProfile
import csv
from datetime import datetime

class Command(BaseCommand):
    help = 'Export all user emails and information to CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='user_emails.csv',
            help='Output CSV filename (default: user_emails.csv)'
        )
        parser.add_argument(
            '--gmail-only',
            action='store_true',
            help='Export only Gmail addresses'
        )

    def handle(self, *args, **options):
        output_file = options['output']
        gmail_only = options['gmail_only']
        
        # Get all users
        users = User.objects.all().select_related('profile')
        
        if gmail_only:
            users = users.filter(email__icontains='@gmail.com')
            self.stdout.write(f'Filtering for Gmail addresses only...')
        
        # Create CSV file
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            fieldnames = [
                'username', 'email', 'first_name', 'last_name', 
                'is_active', 'date_joined', 'last_login',
                'total_donated', 'account_level', 'current_tier'
            ]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            count = 0
            for user in users:
                try:
                    profile = user.profile
                except UserProfile.DoesNotExist:
                    profile = None
                
                writer.writerow({
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name or '',
                    'last_name': user.last_name or '',
                    'is_active': user.is_active,
                    'date_joined': user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else '',
                    'last_login': user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else 'Never',
                    'total_donated': profile.total_donated if profile else 0,
                    'account_level': profile.account_level if profile else 1,
                    'current_tier': profile.current_tier.name if profile and profile.current_tier else 'None'
                })
                count += 1
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully exported {count} users to {output_file}'
            )
        )
        
        # Display summary
        total_users = users.count()
        active_users = users.filter(is_active=True).count()
        gmail_users = users.filter(email__icontains='@gmail.com').count()
        
        self.stdout.write(f'\n📊 Summary:')
        self.stdout.write(f'Total users: {total_users}')
        self.stdout.write(f'Active users: {active_users}')
        self.stdout.write(f'Gmail users: {gmail_users}')
        self.stdout.write(f'Other email providers: {total_users - gmail_users}')
