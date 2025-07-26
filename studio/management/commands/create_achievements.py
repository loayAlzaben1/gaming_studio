from django.core.management.base import BaseCommand
from studio.models import Achievement, AchievementCategory

class Command(BaseCommand):
    help = 'Create initial gaming achievements for the platform'

    def handle(self, *args, **options):
        # Create achievement categories
        categories = [
            {
                'name': 'Donation Champions',
                'description': 'Achievements for supporting the gaming studio',
                'icon': 'fas fa-heart',
                'color': '#FF6B6B'
            },
            {
                'name': 'Social Butterflies', 
                'description': 'Achievements for community engagement',
                'icon': 'fas fa-users',
                'color': '#4ECDC4'
            },
            {
                'name': 'Gaming Masters',
                'description': 'Achievements for gaming prowess',
                'icon': 'fas fa-gamepad',
                'color': '#45B7D1'
            },
            {
                'name': 'Platform Legends',
                'description': 'Special achievements for platform milestones',
                'icon': 'fas fa-crown',
                'color': '#FFA726'
            }
        ]
        
        for cat_data in categories:
            category, created = AchievementCategory.objects.get_or_create(
                name=cat_data['name'],
                defaults=cat_data
            )
            if created:
                self.stdout.write(f"Created category: {category.name}")

        # Create achievements
        achievements = [
            # Donation Achievements
            {
                'type': 'first_donation',
                'name': 'First Supporter',
                'description': 'Made your first donation to support gaming development',
                'icon': 'fas fa-heart',
                'color': '#FF6B6B',
                'experience_reward': 100,
                'is_rare': False
            },
            {
                'type': 'loyal_supporter',
                'name': 'Loyal Supporter',
                'description': 'Made 5 or more donations to the gaming studio',
                'icon': 'fas fa-medal',
                'color': '#FFD700',
                'experience_reward': 200,
                'is_rare': False
            },
            {
                'type': 'big_spender',
                'name': 'Big Spender',
                'description': 'Donated $100 or more in total',
                'icon': 'fas fa-gem',
                'color': '#9B59B6',
                'experience_reward': 300,
                'is_rare': True
            },
            {
                'type': 'monthly_donor',
                'name': 'Monthly Hero',
                'description': 'Set up a monthly recurring donation',
                'icon': 'fas fa-calendar-check',
                'color': '#27AE60',
                'experience_reward': 250,
                'is_rare': False
            },
            
            # Social Achievements
            {
                'type': 'social_butterfly',
                'name': 'Social Butterfly',
                'description': 'Completed your gaming profile with avatar and bio',
                'icon': 'fas fa-user-friends',
                'color': '#4ECDC4',
                'experience_reward': 150,
                'is_rare': False
            },
            {
                'type': 'community_hero',
                'name': 'Community Hero',
                'description': 'Actively engaged with the gaming community',
                'icon': 'fas fa-hands-helping',
                'color': '#FF9F43',
                'experience_reward': 200,
                'is_rare': False
            },
            
            # Gaming Achievements
            {
                'type': 'level_up', 
                'name': 'Level Up Master',
                'description': 'Reached a new experience level',
                'icon': 'fas fa-arrow-up',
                'color': '#45B7D1',
                'experience_reward': 50,
                'is_rare': False
            },
            {
                'type': 'game_enthusiast',
                'name': 'Game Enthusiast',
                'description': 'Played multiple games from our studio',
                'icon': 'fas fa-gamepad',
                'color': '#E74C3C',
                'experience_reward': 175,
                'is_rare': False
            },
            
            # Platform Achievements
            {
                'type': 'early_supporter',
                'name': 'Early Supporter',
                'description': 'One of the first members to join our gaming community',
                'icon': 'fas fa-seedling',
                'color': '#2ECC71',
                'experience_reward': 300,
                'is_rare': True
            },
            {
                'type': 'veteran',
                'name': 'Veteran Member',
                'description': 'Been a member for over 6 months',
                'icon': 'fas fa-shield-alt',
                'color': '#8E44AD',
                'experience_reward': 400,
                'is_rare': True
            },
            
            # Special Achievements
            {
                'type': 'completionist',
                'name': 'Completionist',
                'description': 'Unlocked 75% of all available achievements',
                'icon': 'fas fa-trophy',
                'color': '#FFD700',
                'experience_reward': 500,
                'is_rare': True
            },
            {
                'type': 'perfectionist',
                'name': 'Perfectionist',
                'description': 'Unlocked ALL available achievements',
                'icon': 'fas fa-crown',
                'color': '#FF6B6B',
                'experience_reward': 1000,
                'is_rare': True
            }
        ]
        
        created_count = 0
        for achievement_data in achievements:
            achievement, created = Achievement.objects.get_or_create(
                type=achievement_data['type'],
                defaults=achievement_data
            )
            if created:
                created_count += 1
                self.stdout.write(f"Created achievement: {achievement.name}")
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} new achievements!')
        )
