#!/usr/bin/env python
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaming_studio.settings')
django.setup()

from studio.models import Game, GameForum, ForumTopic, User, UserActivity, UserProfile
from studio.forms import ForumTopicForm

def test_forum_creation():
    print("=== Testing Forum Topic Creation ===")
    
    # Get a game and user
    game = Game.objects.first()
    user = User.objects.first()
    
    if not game:
        print("❌ No games found in database")
        return
    
    if not user:
        print("❌ No users found in database")
        return
        
    print(f"✅ Game: {game.title}")
    print(f"✅ User: {user.username}")
    
    # Get or create forum
    forum, created = GameForum.objects.get_or_create(
        game=game,
        defaults={'name': f'{game.title} Forum', 'description': f'Discussion forum for {game.title}'}
    )
    print(f"✅ Forum: {forum.name} (Created: {created})")
    print(f"   Forum ID: {forum.id}")
    
    # Test form validation
    form_data = {
        'title': 'Debug Test Topic',
        'topic_type': 'discussion',
        'content': 'This is a debug test topic content to check forum functionality.'
    }
    
    form = ForumTopicForm(data=form_data)
    print(f"✅ Form is valid: {form.is_valid()}")
    
    if not form.is_valid():
        print(f"❌ Form errors: {form.errors}")
        return
    
    # Try to create topic
    try:
        topic = form.save(commit=False)
        topic.forum = forum
        topic.author = user
        topic.save()
        print(f"✅ Topic created successfully!")
        print(f"   Topic ID: {topic.id}")
        print(f"   Topic Title: {topic.title}")
        print(f"   Topic Type: {topic.topic_type}")
    except Exception as e:
        print(f"❌ Error creating topic: {e}")
        return
    
    # Test UserActivity creation
    try:
        activity = UserActivity.objects.create(
            user=user,
            activity_type='forum',
            description=f'Started discussion: {topic.title}',
            experience_gained=25
        )
        print(f"✅ UserActivity created: {activity.id}")
    except Exception as e:
        print(f"❌ Error creating UserActivity: {e}")
    
    # Test UserProfile
    try:
        profile, created = UserProfile.objects.get_or_create(user=user)
        print(f"✅ UserProfile: {profile} (Created: {created})")
        
        # Test add_experience method
        initial_exp = profile.experience_points
        profile.add_experience(25)
        print(f"✅ Experience added: {initial_exp} -> {profile.experience_points}")
        
        # Test award_achievement method
        profile.award_achievement('discussion_starter')
        print(f"✅ Achievement awarded")
        
    except Exception as e:
        print(f"❌ Error with UserProfile: {e}")
    
    # Check if topic appears in forum
    topics_count = forum.topics.count()
    print(f"✅ Forum now has {topics_count} topics")
    
    # Test URL reverse
    from django.urls import reverse
    try:
        topic_url = reverse('forum_topic', kwargs={'topic_id': topic.id})
        print(f"✅ Topic URL: {topic_url}")
    except Exception as e:
        print(f"❌ Error reversing URL: {e}")
    
    print("\n=== Debug Complete ===")
    print("If all tests passed, the issue might be in the view logic or template.")

if __name__ == "__main__":
    test_forum_creation()
