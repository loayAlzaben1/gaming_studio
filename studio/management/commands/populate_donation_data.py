from django.core.management.base import BaseCommand
from decimal import Decimal
from studio.models import SponsorTier, DonationGoal


class Command(BaseCommand):
    help = 'Populates default sponsor tiers and donation goals for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating default sponsor tiers...')
        
        # Create sponsor tiers if they don't exist
        tiers_data = [
            {
                'name': 'bronze',
                'min_amount': Decimal('5.00'),
                'color': '#CD7F32',
                'perks': 'Access to development updates\nCommunity Discord access',
                'icon': 'fas fa-medal'
            },
            {
                'name': 'silver',
                'min_amount': Decimal('25.00'),
                'color': '#C0C0C0',
                'perks': 'Bronze perks\nEarly access to beta builds\nMonthly Q&A sessions',
                'icon': 'fas fa-trophy'
            },
            {
                'name': 'gold',
                'min_amount': Decimal('100.00'),
                'color': '#FFD700',
                'perks': 'Silver perks\nName in game credits\nExclusive game content\nPriority support',
                'icon': 'fas fa-crown'
            },
            {
                'name': 'platinum',
                'min_amount': Decimal('250.00'),
                'color': '#E5E4E2',
                'perks': 'Gold perks\nDirect developer access\nInfluence on game features\nSigned merchandise',
                'icon': 'fas fa-gem'
            },
            {
                'name': 'diamond',
                'min_amount': Decimal('500.00'),
                'color': '#B9F2FF',
                'perks': 'Platinum perks\nExecutive producer credit\nQuarterly studio visits\nCustom character design',
                'icon': 'fas fa-diamond'
            }
        ]

        for tier_data in tiers_data:
            tier, created = SponsorTier.objects.get_or_create(
                name=tier_data['name'],
                defaults=tier_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created sponsor tier: {tier.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Sponsor tier already exists: {tier.name}')
                )

        self.stdout.write('\nCreating default donation goals...')
        
        # Create donation goals if they don't exist
        goals_data = [
            {
                'title': 'New Gaming Equipment',
                'description': 'Help us upgrade our development hardware for better game performance testing and development.',
                'target_amount': Decimal('5000.00'),
                'current_amount': Decimal('1250.00'),
                'status': 'active'
            },
            {
                'title': 'Community Events Fund',
                'description': 'Support our quarterly community gaming tournaments and meetups.',
                'target_amount': Decimal('2500.00'),
                'current_amount': Decimal('750.00'),
                'status': 'active'
            },
            {
                'title': 'Studio Expansion',
                'description': 'Help us grow our team and expand our studio space for bigger projects.',
                'target_amount': Decimal('25000.00'),
                'current_amount': Decimal('8500.00'),
                'status': 'active'
            },
            {
                'title': 'Open Source Tools',
                'description': 'Fund the development of open-source game development tools for the community.',
                'target_amount': Decimal('10000.00'),
                'current_amount': Decimal('3200.00'),
                'status': 'paused'
            }
        ]

        for goal_data in goals_data:
            goal, created = DonationGoal.objects.get_or_create(
                title=goal_data['title'],
                defaults=goal_data
            )
            if created:
                self.stdout.write(
                    self.style.SUCCESS(f'Created donation goal: {goal.title}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Donation goal already exists: {goal.title}')
                )

        self.stdout.write('\n' + self.style.SUCCESS('Successfully populated donation data!'))
        self.stdout.write('You can now test the advanced donation features.')
