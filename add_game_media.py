#!/usr/bin/env python
"""
Script to add game screenshots and media content to showcase enhanced display
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaming_studio.settings')
django.setup()

from studio.models import Game, Photo, Video

def add_game_media():
    """Add diverse media content to games"""
    
    print("📸 Adding Game Screenshots and Media...")
    
    # Media content for different games
    media_data = {
        '🎯 Cyber Nexus: Arena Combat': {
            'photos': [
                {
                    'caption': 'Intense 5v5 arena combat with cyberpunk aesthetics',
                    'description': 'Main combat arena showing neon-lit environment'
                },
                {
                    'caption': 'Character customization screen with unique abilities',
                    'description': 'Extensive character creation system'
                },
                {
                    'caption': 'Weapon customization and loadout selection',
                    'description': 'Advanced weapon modification interface'
                }
            ],
            'videos': [
                {
                    'title': 'Cyber Nexus Official Gameplay Trailer',
                    'video_url': 'https://www.youtube.com/embed/dQw4w9WgXcQ'  # Placeholder URL
                },
                {
                    'title': 'Arena Combat Highlights - Best Plays',
                    'video_url': 'https://www.youtube.com/embed/oHg5SJYRHA0'  # Placeholder URL
                }
            ]
        },
        '🏰 Medieval Kingdoms: Strategy Edition': {
            'photos': [
                {
                    'caption': 'Epic castle sieges with realistic medieval warfare',
                    'description': 'Large-scale battle with siege weapons'
                },
                {
                    'caption': 'Detailed kingdom management interface',
                    'description': 'Resource management and city building'
                },
                {
                    'caption': 'Diplomatic negotiations with neighboring kingdoms',
                    'description': 'Complex diplomacy system in action'
                }
            ],
            'videos': [
                {
                    'title': 'Medieval Kingdoms - Strategy Deep Dive',
                    'video_url': 'https://www.youtube.com/embed/jNQXAC9IVRw'  # Placeholder URL
                }
            ]
        },
        '🌙 Moonlight Chronicles: RPG Adventure': {
            'photos': [
                {
                    'caption': 'Mystical fantasy landscapes under moonlight',
                    'description': 'Atmospheric world design with magical elements'
                },
                {
                    'caption': 'Character progression and spell crafting system',
                    'description': 'RPG mechanics showing character development'
                }
            ],
            'videos': [
                {
                    'title': 'Moonlight Chronicles - World Exploration',
                    'video_url': 'https://www.youtube.com/embed/9bZkp7q19f0'  # Placeholder URL
                }
            ]
        },
        '🏎️ Velocity Racing: Mobile Edition': {
            'photos': [
                {
                    'caption': 'High-speed racing on mobile with console-quality graphics',
                    'description': 'Mobile-optimized racing interface'
                },
                {
                    'caption': 'Vehicle customization garage',
                    'description': 'Extensive car modification system'
                }
            ],
            'videos': [
                {
                    'title': 'Velocity Racing Mobile - Championship Mode',
                    'video_url': 'https://www.youtube.com/embed/ScMzIvxBSi4'  # Placeholder URL
                }
            ]
        }
    }
    
    # Process each game's media
    for game_title, media in media_data.items():
        try:
            game = Game.objects.get(title=game_title)
            print(f"\n🎮 Processing media for: {game.title}")
            
            # Add photos
            photos_added = 0
            for photo_data in media.get('photos', []):
                # Check if photo already exists
                existing_photo = Photo.objects.filter(
                    game=game, 
                    caption=photo_data['caption']
                ).first()
                
                if not existing_photo:
                    photo = Photo.objects.create(
                        game=game,
                        caption=photo_data['caption']
                        # Note: We're not adding actual image files for this demo
                    )
                    photos_added += 1
                    print(f"   📷 Added photo: {photo.caption}")
                else:
                    print(f"   📷 Photo already exists: {photo_data['caption']}")
            
            # Add videos
            videos_added = 0
            for video_data in media.get('videos', []):
                # Check if video already exists
                existing_video = Video.objects.filter(
                    game=game,
                    title=video_data['title']
                ).first()
                
                if not existing_video:
                    video = Video.objects.create(
                        game=game,
                        title=video_data['title'],
                        video_url=video_data['video_url']
                    )
                    videos_added += 1
                    print(f"   🎬 Added video: {video.title}")
                else:
                    print(f"   🎬 Video already exists: {video_data['title']}")
            
            print(f"   ✅ Added {photos_added} photos and {videos_added} videos")
            
        except Game.DoesNotExist:
            print(f"   ⚠️  Game not found: {game_title}")
    
    # Media summary
    print(f"\n📊 Media Content Summary:")
    total_photos = Photo.objects.count()
    total_videos = Video.objects.count()
    
    print(f"   Total Photos: {total_photos}")
    print(f"   Total Videos: {total_videos}")
    
    # Show games with media content
    print(f"\n🎨 Games with Media Content:")
    for game in Game.objects.all():
        photo_count = game.photo_set.count()
        video_count = game.video_set.count()
        if photo_count > 0 or video_count > 0:
            print(f"   🎮 {game.title}")
            print(f"      Photos: {photo_count}, Videos: {video_count}")
    
    # Featured games with media showcase
    print(f"\n⭐ Featured Games Media Showcase:")
    featured_games = Game.objects.filter(is_featured=True).order_by('featured_order')
    for game in featured_games:
        photo_count = game.photo_set.count()
        video_count = game.video_set.count()
        print(f"   🌟 {game.title}")
        print(f"      Media: {photo_count} photos, {video_count} videos")
        print(f"      Status: {game.get_status_display()}")
        print(f"      Platform: {game.get_platform_display()}")

if __name__ == '__main__':
    add_game_media()
