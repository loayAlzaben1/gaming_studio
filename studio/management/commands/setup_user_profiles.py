from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from studio.models import UserProfile
from datetime import timedelta
from django.utils import timezone

class Command(BaseCommand):
    help = 'Update existing users with gaming profiles and award early supporter achievements'

    def handle(self, *args, **options):
        updated_count = 0
        
        # Get all existing users
        users = User.objects.all()
        
        for user in users:
            # Get or create user profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            if created or not profile.join_date:
                # Set join date for new profiles
                profile.join_date = user.date_joined
                profile.save()
                updated_count += 1
                
                # Award early supporter achievement if user joined recently
                if user.date_joined >= timezone.now() - timedelta(days=30):
                    profile.award_achievement('early_supporter')
                    self.stdout.write(
                        self.style.SUCCESS(f'Awarded early supporter to: {user.username}')
                    )
                
                self.stdout.write(
                    self.style.SUCCESS(f'Created profile for: {user.username}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Profile already exists for: {user.username}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully processed {len(users)} users, updated {updated_count} profiles!')
        )
