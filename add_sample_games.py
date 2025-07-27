#!/usr/bin/env python
"""
Script to add diverse sample games to showcase the enhanced game management system
"""
import os
import django
from datetime import date

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaming_studio.settings')
django.setup()

from studio.models import Game
from django.contrib.auth.models import User

def add_sample_games():
    """Add diverse sample games with different platforms and statuses"""
    
    # Get the admin user for games (or create if needed)
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        print("No admin user found. Creating one...")
        admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    
    # Sample games data with diverse platforms and statuses
    games_data = [
        {
            'title': '🎯 Cyber Nexus: Arena Combat',
            'description': 'Fast-paced multiplayer arena shooter set in a cyberpunk world. Battle against players worldwide in intense 5v5 matches with unique character abilities and customizable weapons.',
            'platform': 'cross_platform',
            'genre': 'fps',
            'status': 'released',
            'is_featured': True,
            'release_date': date(2024, 12, 15),
            'age_rating': 'teen',
            'min_players': 1,
            'max_players': 10,
            'estimated_playtime': 120
        },
        {
            'title': '🏰 Medieval Kingdoms: Strategy Edition',
            'description': 'Build your empire from a small village to a mighty kingdom. Manage resources, conduct diplomacy, and lead epic battles in this comprehensive strategy game.',
            'platform': 'pc',
            'genre': 'strategy',
            'status': 'beta',
            'is_featured': True,
            'release_date': date(2025, 9, 1),
            'age_rating': 'everyone_10',
            'min_players': 1,
            'max_players': 8,
            'estimated_playtime': 480
        },
        {
            'title': '🌙 Moonlight Chronicles: RPG Adventure',
            'description': 'Embark on an epic fantasy journey through mystical lands. Create your character, master magical abilities, and uncover the secrets of the ancient moonlight prophecy.',
            'platform': 'console',
            'genre': 'rpg',
            'status': 'development',
            'is_featured': False,
            'release_date': date(2025, 12, 20),
            'age_rating': 'teen',
            'min_players': 1,
            'max_players': 4,
            'estimated_playtime': 1200
        },
        {
            'title': '🏎️ Velocity Racing: Mobile Edition',
            'description': 'High-speed racing action optimized for mobile devices. Race through stunning environments, customize your vehicles, and compete in championship tournaments.',
            'platform': 'mobile',
            'genre': 'racing',
            'status': 'released',
            'is_featured': False,
            'release_date': date(2024, 8, 10),
            'age_rating': 'everyone',
            'min_players': 1,
            'max_players': 12,
            'estimated_playtime': 60
        },
        {
            'title': '🎵 Rhythm Masters: Music Game',
            'description': 'Feel the beat and master the rhythm in this musical adventure. Play along to popular tracks, create custom beats, and challenge friends in rhythm battles.',
            'platform': 'cross_platform',
            'genre': 'music',
            'status': 'alpha',
            'is_featured': False,
            'release_date': date(2025, 11, 15),
            'age_rating': 'everyone',
            'min_players': 1,
            'max_players': 6,
            'estimated_playtime': 90
        },
        {
            'title': '🚀 Space Odyssey: Exploration Simulator',
            'description': 'Explore the vast cosmos in this realistic space simulation. Build spacecraft, discover new planets, and establish colonies across the galaxy.',
            'platform': 'pc',
            'genre': 'simulation',
            'status': 'concept',
            'is_featured': False,
            'release_date': date(2026, 3, 15),
            'age_rating': 'everyone_10',
            'min_players': 1,
            'max_players': 1,
            'estimated_playtime': 600
        }
    ]
    
    # Create the games
    created_games = []
    for game_data in games_data:
        # Check if game already exists
        existing_game = Game.objects.filter(title=game_data['title']).first()
        if existing_game:
            print(f"⚠️  Game already exists: {game_data['title']}")
            continue
            
        game = Game.objects.create(**game_data)
        created_games.append(game)
        print(f"✅ Created: {game.title}")
        print(f"   Platform: {game.get_platform_display()}")
        print(f"   Genre: {game.get_genre_display()}")
        print(f"   Status: {game.get_status_display()}")
        print(f"   Featured: {'Yes' if game.is_featured else 'No'}")
        print("   " + "="*50)
    
    print(f"\n🎮 Successfully created {len(created_games)} new games!")
    print(f"📊 Total games in database: {Game.objects.count()}")
    
    # Show summary by platform
    print("\n📱 Games by Platform:")
    for platform_code, platform_name in Game.PLATFORM_CHOICES:
        count = Game.objects.filter(platform=platform_code).count()
        if count > 0:
            print(f"   {platform_name}: {count} games")
    
    # Show summary by status
    print("\n⚡ Games by Status:")
    for status_code, status_name in Game.STATUS_CHOICES:
        count = Game.objects.filter(status=status_code).count()
        if count > 0:
            print(f"   {status_name}: {count} games")
    
    # Show featured games
    featured_count = Game.objects.filter(is_featured=True).count()
    print(f"\n⭐ Featured games: {featured_count}")

if __name__ == '__main__':
    add_sample_games()
