#!/usr/bin/env python
"""
Script to set up featured games and test the showcase priority system
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaming_studio.settings')
django.setup()

from studio.models import Game

def setup_featured_games():
    """Set up featured games with different priorities"""
    
    print("🌟 Setting up Featured Games...")
    
    # Featured games configuration
    featured_games_config = [
        {
            'title': '🎯 Cyber Nexus: Arena Combat',
            'is_featured': True,
            'featured_order': 1,
            'reason': 'New multiplayer release - high priority'
        },
        {
            'title': '🏰 Medieval Kingdoms: Strategy Edition',
            'is_featured': True,
            'featured_order': 2,
            'reason': 'Beta release - showcase strategy'
        },
        {
            'title': '⚔️ Welcome to the War of Tomorrow – Experience the Rise of NERO ⚙️',
            'is_featured': True,
            'featured_order': 3,
            'reason': 'Main game in development'
        },
        # Make sure some games are not featured to show contrast
        {
            'title': '🌙 Moonlight Chronicles: RPG Adventure',
            'is_featured': False,
            'featured_order': 0,
            'reason': 'Still in development - not ready for spotlight'
        }
    ]
    
    updated_games = []
    for config in featured_games_config:
        try:
            game = Game.objects.get(title=config['title'])
            
            # Update featured status and order
            game.is_featured = config['is_featured']
            game.featured_order = config['featured_order']
            game.save(update_fields=['is_featured', 'featured_order'])
            
            updated_games.append(game)
            status = "✅ FEATURED" if config['is_featured'] else "⭕ NOT FEATURED"
            print(f"{status}: {game.title}")
            print(f"   Priority: {config['featured_order']}")
            print(f"   Reason: {config['reason']}")
            print("   " + "="*60)
            
        except Game.DoesNotExist:
            print(f"⚠️  Game not found: {config['title']}")
    
    # Show featured games summary
    print(f"\n🎮 Featured Games Summary:")
    featured_games = Game.objects.filter(is_featured=True).order_by('featured_order')
    for i, game in enumerate(featured_games, 1):
        print(f"   {i}. {game.title}")
        print(f"      Platform: {game.get_platform_display()}")
        print(f"      Status: {game.get_status_display()}")
        print(f"      Priority Order: {game.featured_order}")
    
    print(f"\n📊 Games Statistics:")
    total_games = Game.objects.count()
    featured_count = Game.objects.filter(is_featured=True).count()
    released_count = Game.objects.filter(status='released').count()
    in_dev_count = Game.objects.filter(status='development').count()
    beta_count = Game.objects.filter(status='beta').count()
    
    print(f"   Total Games: {total_games}")
    print(f"   Featured Games: {featured_count}")
    print(f"   Released Games: {released_count}")
    print(f"   In Development: {in_dev_count}")
    print(f"   Beta Games: {beta_count}")
    
    # Test the homepage showcase
    print(f"\n🏠 Homepage Showcase (Featured Games Order):")
    homepage_games = Game.objects.filter(is_featured=True).order_by('featured_order')
    for game in homepage_games:
        print(f"   → {game.title} (Order: {game.featured_order})")
    
    return updated_games

if __name__ == '__main__':
    setup_featured_games()
