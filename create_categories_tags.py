#!/usr/bin/env python
"""
Script to create game categories and tags for filtering system
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaming_studio.settings')
django.setup()

from studio.models import Game, GameCategory, GameTag

def create_categories_and_tags():
    """Create comprehensive categories and tags for game filtering"""
    
    # Create Game Categories
    categories_data = [
        {
            'name': 'Action Games',
            'description': 'Fast-paced games requiring quick reflexes and hand-eye coordination',
            'color': '#FF6B6B'
        },
        {
            'name': 'Strategy Games',
            'description': 'Games that emphasize skillful thinking and planning',
            'color': '#4ECDC4'
        },
        {
            'name': 'RPG Adventures',
            'description': 'Role-playing games with character development and storytelling',
            'color': '#45B7D1'
        },
        {
            'name': 'Racing & Sports',
            'description': 'Competitive racing and sports simulation games',
            'color': '#96CEB4'
        },
        {
            'name': 'Puzzle & Music',
            'description': 'Brain teasers, rhythm games, and creative challenges',
            'color': '#FFEAA7'
        },
        {
            'name': 'Simulation',
            'description': 'Realistic simulations of real-world activities',
            'color': '#DDA0DD'
        }
    ]
    
    # Create Game Tags
    tags_data = [
        # Platform-specific tags
        {'name': 'PC Gaming'},
        {'name': 'Console'},
        {'name': 'Mobile Gaming'},
        {'name': 'Cross-Platform'},
        
        # Genre-specific tags
        {'name': 'Multiplayer'},
        {'name': 'Single Player'},
        {'name': 'Co-op'},
        {'name': 'Competitive'},
        
        # Feature tags
        {'name': 'Open World'},
        {'name': 'Story Rich'},
        {'name': 'Character Customization'},
        {'name': 'Real-time Strategy'},
        {'name': 'Turn-based'},
        {'name': 'Sandbox'},
        
        # Age and difficulty tags
        {'name': 'Family Friendly'},
        {'name': 'Hardcore'},
        {'name': 'Casual'},
        {'name': 'Indie'},
        
        # Special features
        {'name': 'VR Ready'},
        {'name': 'Early Access'},
        {'name': 'Free to Play'},
        {'name': 'Premium'}
    ]
    
    print("🏷️  Creating Game Categories...")
    created_categories = []
    for cat_data in categories_data:
        category, created = GameCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'color': cat_data['color'],
                'slug': cat_data['name'].lower().replace(' ', '-').replace('&', 'and')
            }
        )
        if created:
            created_categories.append(category)
            print(f"✅ Created category: {category.name}")
        else:
            print(f"⚠️  Category already exists: {category.name}")
    
    print(f"\n🎯 Creating Game Tags...")
    created_tags = []
    for tag_data in tags_data:
        tag, created = GameTag.objects.get_or_create(
            name=tag_data['name'],
            defaults={
                'slug': tag_data['name'].lower().replace(' ', '-')
            }
        )
        if created:
            created_tags.append(tag)
            print(f"✅ Created tag: {tag.name}")
        else:
            print(f"⚠️  Tag already exists: {tag.name}")
    
    print(f"\n🎮 Assigning Categories and Tags to Games...")
    
    # Assign categories and tags to existing games
    games_assignments = {
        '🎯 Cyber Nexus: Arena Combat': {
            'categories': ['Action Games'],
            'tags': ['PC Gaming', 'Cross-Platform', 'Multiplayer', 'Competitive', 'Hardcore']
        },
        '🏰 Medieval Kingdoms: Strategy Edition': {
            'categories': ['Strategy Games'],
            'tags': ['PC Gaming', 'Single Player', 'Real-time Strategy', 'Sandbox', 'Indie']
        },
        '🌙 Moonlight Chronicles: RPG Adventure': {
            'categories': ['RPG Adventures'],
            'tags': ['Console', 'Single Player', 'Co-op', 'Open World', 'Story Rich', 'Character Customization']
        },
        '🏎️ Velocity Racing: Mobile Edition': {
            'categories': ['Racing & Sports'],
            'tags': ['Mobile Gaming', 'Multiplayer', 'Competitive', 'Casual', 'Family Friendly']
        },
        '🎵 Rhythm Masters: Music Game': {
            'categories': ['Puzzle & Music'],
            'tags': ['Cross-Platform', 'Multiplayer', 'Casual', 'Family Friendly', 'Early Access']
        },
        '🚀 Space Odyssey: Exploration Simulator': {
            'categories': ['Simulation'],
            'tags': ['PC Gaming', 'Single Player', 'Open World', 'Sandbox', 'Indie']
        }
    }
    
    for game_title, assignments in games_assignments.items():
        try:
            game = Game.objects.get(title=game_title)
            
            # Assign categories
            for cat_name in assignments.get('categories', []):
                category = GameCategory.objects.get(name=cat_name)
                game.categories.add(category)
            
            # Assign tags
            for tag_name in assignments.get('tags', []):
                tag = GameTag.objects.get(name=tag_name)
                tag.games.add(game)  # Add game to tag's games
            
            print(f"✅ Assigned categories and tags to: {game_title}")
            
        except Game.DoesNotExist:
            print(f"⚠️  Game not found: {game_title}")
        except (GameCategory.DoesNotExist, GameTag.DoesNotExist) as e:
            print(f"⚠️  Assignment error for {game_title}: {e}")
    
    # Summary
    print(f"\n📊 Summary:")
    print(f"   Categories created: {len(created_categories)}")
    print(f"   Tags created: {len(created_tags)}")
    print(f"   Total categories: {GameCategory.objects.count()}")
    print(f"   Total tags: {GameTag.objects.count()}")
    
    # Show categories with game counts
    print(f"\n🗂️  Categories with game counts:")
    for category in GameCategory.objects.all():
        game_count = category.games.count()
        print(f"   {category.name}: {game_count} games")
    
    # Show most popular tags
    print(f"\n🏷️  Popular tags:")
    for tag in GameTag.objects.all()[:10]:
        game_count = tag.games.count()
        if game_count > 0:
            print(f"   {tag.name}: {game_count} games")

if __name__ == '__main__':
    create_categories_and_tags()
