from django.core.management.base import BaseCommand
from studio.models import Achievement

class Command(BaseCommand):
    help = 'Create initial achievements for the gaming studio'

    def handle(self, *args, **options):
        achievements = [
            {
                'type': 'first_donation',
                'name': 'First Steps',
                'description': 'Made your first donation to support the gaming studio!',
                'icon': 'fas fa-heart',
                'color': '#FF6B6B',
                'experience_reward': 100,
                'is_rare': False,
            },
            {
                'type': 'loyal_supporter',
                'name': 'Loyal Supporter',
                'description': 'Made 5 or more donations. Your loyalty is amazing!',
                'icon': 'fas fa-medal',
                'color': '#4ECDC4',
                'experience_reward': 200,
                'is_rare': False,
            },
            {
                'type': 'big_spender',
                'name': 'Big Spender',
                'description': 'Donated $100 or more in total. You\'re incredible!',
                'icon': 'fas fa-gem',
                'color': '#9B59B6',
                'experience_reward': 300,
                'is_rare': True,
            },
            {
                'type': 'level_up',
                'name': 'Level Master',
                'description': 'Reached a new account level through gaming activities!',
                'icon': 'fas fa-arrow-up',
                'color': '#F39C12',
                'experience_reward': 50,
                'is_rare': False,
            },
            {
                'type': 'community_hero',
                'name': 'Community Hero',
                'description': 'Actively participated in community discussions!',
                'icon': 'fas fa-users',
                'color': '#2ECC71',
                'experience_reward': 150,
                'is_rare': False,
            },
            {
                'type': 'early_supporter',
                'name': 'Early Adopter',
                'description': 'One of the first members to join Gaming Studio!',
                'icon': 'fas fa-rocket',
                'color': '#E74C3C',
                'experience_reward': 250,
                'is_rare': True,
            },
            {
                'type': 'monthly_donor',
                'name': 'Monthly Champion',
                'description': 'Set up a monthly recurring donation. You\'re amazing!',
                'icon': 'fas fa-calendar-check',
                'color': '#3498DB',
                'experience_reward': 200,
                'is_rare': False,
            },
            {
                'type': 'game_enthusiast',
                'name': 'Game Enthusiast',
                'description': 'Showed interest in multiple games and content!',
                'icon': 'fas fa-gamepad',
                'color': '#FF9F43',
                'experience_reward': 100,
                'is_rare': False,
            },
            {
                'type': 'social_butterfly',
                'name': 'Social Butterfly',
                'description': 'Connected multiple social accounts and stayed active!',
                'icon': 'fas fa-share-alt',
                'color': '#00D2D3',
                'experience_reward': 150,
                'is_rare': False,
            },
            {
                'type': 'veteran',
                'name': 'Veteran Member',
                'description': 'Been a member for over 6 months. Welcome to the family!',
                'icon': 'fas fa-crown',
                'color': '#FFD700',
                'experience_reward': 500,
                'is_rare': True,
            },
        ]

        created_count = 0
        for achievement_data in achievements:
            achievement, created = Achievement.objects.get_or_create(
                type=achievement_data['type'],
                defaults=achievement_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created achievement: {achievement.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Achievement already exists: {achievement.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new achievements!')
        )
