from django.core.management.base import BaseCommand
from studio.models import Game

class Command(BaseCommand):
    help = 'Add sample game immediately'

    def handle(self, *args, **options):
        # Delete existing games and add fresh ones
        Game.objects.all().delete()
        
        games_data = [
            {
                'title': 'RTS Strategy Game',
                'description': 'An epic real-time strategy game with immersive gameplay and stunning graphics.',
                'is_featured': True
            },
            {
                'title': 'Action Adventure',
                'description': 'Thrilling action-packed adventure with amazing storyline.',
                'is_featured': False
            }
        ]
        
        for game_data in games_data:
            game = Game.objects.create(**game_data)
            self.stdout.write(f"✅ Created: {game.title}")
        
        count = Game.objects.count()
        self.stdout.write(self.style.SUCCESS(f"🎉 Total games: {count}"))
