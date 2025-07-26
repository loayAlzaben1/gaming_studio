from django.db import models
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

# User Profile for extended user information
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    total_donated = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    current_tier = models.ForeignKey('SponsorTier', on_delete=models.SET_NULL, null=True, blank=True)
    join_date = models.DateTimeField(auto_now_add=True)
    is_premium = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, default='avatars/default.png')
    bio = models.TextField(max_length=500, blank=True)
    
    # Gaming Stats
    total_donations_count = models.IntegerField(default=0)
    favorite_game = models.ForeignKey('Game', on_delete=models.SET_NULL, null=True, blank=True)
    account_level = models.IntegerField(default=1)
    experience_points = models.IntegerField(default=0)
    login_streak = models.IntegerField(default=0)
    last_login_date = models.DateField(null=True, blank=True)
    
    # Social Stats
    profile_views = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    likes_received = models.IntegerField(default=0)
    
    # Enhanced Gaming Features
    gaming_style = models.CharField(max_length=50, choices=[
        ('casual', 'Casual Gamer'),
        ('hardcore', 'Hardcore Gamer'),
        ('competitive', 'Competitive Player'),
        ('story_lover', 'Story Enthusiast'),
        ('multiplayer', 'Multiplayer Focused'),
        ('indie_supporter', 'Indie Game Supporter'),
    ], default='casual', blank=True)
    
    preferred_platforms = models.CharField(max_length=200, blank=True, help_text="Comma-separated list of preferred gaming platforms")
    favorite_genres = models.CharField(max_length=200, blank=True, help_text="Comma-separated list of favorite game genres")
    gaming_hours_weekly = models.IntegerField(default=0, help_text="Average gaming hours per week")
    
    # Profile Customization
    theme_preference = models.CharField(max_length=20, choices=[
        ('dark', 'Dark Theme'),
        ('light', 'Light Theme'),
        ('auto', 'Auto Theme'),
        ('gaming', 'Gaming Theme'),
        ('neon', 'Neon Theme'),
    ], default='dark')
    
    profile_banner = models.ImageField(upload_to='profile_banners/', null=True, blank=True)
    custom_title = models.CharField(max_length=100, blank=True, help_text="Custom title to display on profile")
    is_profile_public = models.BooleanField(default=True)
    
    # Social Features
    followers = models.ManyToManyField('self', through='UserFollow', symmetrical=False, related_name='following_users')
    
    # Achievement Display
    featured_achievements = models.ManyToManyField('Achievement', through='FeaturedAchievement', blank=True, related_name='featured_by_users')
    
    def update_tier(self):
        """Update user's tier based on total donations"""
        if self.total_donated > 0:
            tier = SponsorTier.objects.filter(min_amount__lte=self.total_donated).order_by('-min_amount').first()
            if tier:
                self.current_tier = tier
                self.is_premium = True
                self.save()
    
    def calculate_level(self):
        """Calculate user level based on experience points"""
        # Level up every 100 XP
        new_level = max(1, (self.experience_points // 100) + 1)
        if new_level != self.account_level:
            self.account_level = new_level
            self.save()
            # Award level up achievement
            self.award_achievement('level_up')
        return new_level
    
    def add_experience(self, points):
        """Add experience points and check for level up"""
        self.experience_points += points
        self.calculate_level()
        self.save()
    
    def award_achievement(self, achievement_type):
        """Award an achievement to the user"""
        try:
            achievement = Achievement.objects.get(type=achievement_type)
            user_achievement, created = UserAchievement.objects.get_or_create(
                user=self.user,
                achievement=achievement,
                defaults={'earned_date': timezone.now()}
            )
            if created:
                self.add_experience(achievement.experience_reward)
                return True
        except Achievement.DoesNotExist:
            pass
        return False
    
    def get_next_level_progress(self):
        """Get progress towards next level as percentage"""
        current_level_xp = (self.account_level - 1) * 100
        next_level_xp = self.account_level * 100
        progress_xp = self.experience_points - current_level_xp
        total_needed = next_level_xp - current_level_xp
        return (progress_xp / total_needed) * 100 if total_needed > 0 else 0
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - Level {self.account_level} - {self.current_tier.get_name_display() if self.current_tier else 'No Tier'}"

class Game(models.Model):
    PLATFORM_CHOICES = [
        ('pc', 'PC'),
        ('playstation', 'PlayStation'),
        ('xbox', 'Xbox'),
        ('nintendo', 'Nintendo Switch'),
        ('mobile', 'Mobile'),
        ('web', 'Web Browser'),
        ('vr', 'Virtual Reality'),
        ('multiple', 'Multi-Platform'),
    ]
    
    GENRE_CHOICES = [
        ('action', 'Action'),
        ('adventure', 'Adventure'),
        ('rpg', 'RPG'),
        ('strategy', 'Strategy'),
        ('simulation', 'Simulation'),
        ('puzzle', 'Puzzle'),
        ('horror', 'Horror'),
        ('racing', 'Racing'),
        ('sports', 'Sports'),
        ('fighting', 'Fighting'),
        ('shooter', 'Shooter'),
        ('platformer', 'Platformer'),
        ('mmorpg', 'MMORPG'),
        ('indie', 'Indie'),
        ('casual', 'Casual'),
    ]
    
    STATUS_CHOICES = [
        ('development', 'In Development'),
        ('alpha', 'Alpha'),
        ('beta', 'Beta'),
        ('released', 'Released'),
        ('coming_soon', 'Coming Soon'),
        ('early_access', 'Early Access'),
        ('cancelled', 'Cancelled'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    short_description = models.CharField(max_length=300, blank=True, help_text="Brief description for cards and previews")
    platform = models.CharField(max_length=100, choices=PLATFORM_CHOICES, default='pc')
    genre = models.CharField(max_length=50, choices=GENRE_CHOICES, default='action')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='development')
    release_date = models.DateField()
    cover_image = models.ImageField(upload_to='game_covers/', null=True, blank=True)
    trailer_link = models.URLField(max_length=200, null=True, blank=True)
    photos = models.ManyToManyField('Photo', related_name='games', blank=True)
    videos = models.ManyToManyField('Video', related_name='games', blank=True)
    is_featured = models.BooleanField(default=False, help_text="Designates whether this game is featured on the home page.")
    
    # Enhanced Game Features
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    total_reviews = models.IntegerField(default=0)
    play_count = models.IntegerField(default=0, help_text="Number of times this game has been played")
    wishlist_count = models.IntegerField(default=0)
    download_count = models.IntegerField(default=0)
    
    # Game Details
    min_players = models.IntegerField(default=1)
    max_players = models.IntegerField(default=1)
    estimated_playtime = models.CharField(max_length=50, blank=True, help_text="e.g., '2-4 hours', '50+ hours'")
    age_rating = models.CharField(max_length=10, choices=[
        ('E', 'Everyone'),
        ('E10+', 'Everyone 10+'),
        ('T', 'Teen'),
        ('M', 'Mature 17+'),
        ('AO', 'Adults Only'),
        ('RP', 'Rating Pending'),
    ], default='E', blank=True)
    
    # SEO and Discovery
    tags = models.CharField(max_length=300, blank=True, help_text="Comma-separated tags for better discovery")
    featured_order = models.IntegerField(default=0, help_text="Order for featured games (0 = not featured)")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['genre']),
            models.Index(fields=['platform']),
            models.Index(fields=['-average_rating']),
            models.Index(fields=['-featured_order']),
        ]
    
    def get_rating_display(self):
        """Get star rating display"""
        if self.average_rating > 0:
            return f"{self.average_rating}/5.0"
        return "No ratings yet"
    
    def get_tag_list(self):
        """Get tags as a list"""
        if self.tags:
            return [tag.strip() for tag in self.tags.split(',')]
        return []
    
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('game_detail', kwargs={'pk': self.pk})
    
    def update_average_rating(self):
        """Update average rating based on reviews"""
        reviews = self.reviews.all()
        if reviews.exists():
            total_rating = sum(review.rating for review in reviews)
            self.average_rating = round(total_rating / reviews.count(), 2)
            self.total_reviews = reviews.count()
        else:
            self.average_rating = 0.00
            self.total_reviews = 0
        self.save(update_fields=['average_rating', 'total_reviews'])
    
    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"

class Photo(models.Model):
    image = models.ImageField(upload_to='game_photos/')
    caption = models.CharField(max_length=200, blank=True)
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='photo_set')

    def __str__(self):
        return self.caption or f"Photo for {self.game.title}"

class Video(models.Model):
    title = models.CharField(max_length=200)
    video_url = models.URLField(max_length=500, help_text="Enter a YouTube embed URL (e.g., https://www.youtube.com/embed/...)")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='video_set')

    def __str__(self):
        return self.title

class DevlogVideo(models.Model):
    title = models.CharField(max_length=200)
    video_url = models.URLField(max_length=200)
    description = models.TextField(blank=True)
    game = models.ForeignKey('Game', related_name='devlog_video_entries', on_delete=models.CASCADE)
    content = models.TextField()
    author = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='team_photos/', null=True, blank=True)
    social_link = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name

# Advanced Donation System Models

class SponsorTier(models.Model):
    TIER_CHOICES = [
        ('bronze', 'Bronze Supporter'),
        ('silver', 'Silver Supporter'), 
        ('gold', 'Gold Supporter'),
        ('platinum', 'Platinum Supporter'),
        ('diamond', 'Diamond Supporter'),
    ]
    
    name = models.CharField(max_length=20, choices=TIER_CHOICES, unique=True)
    min_amount = models.DecimalField(max_digits=10, decimal_places=2)
    color = models.CharField(max_length=7, default='#6B7280')  # Hex color
    perks = models.TextField(help_text="List of perks for this tier, one per line")
    icon = models.CharField(max_length=50, default='fas fa-heart', help_text="FontAwesome icon class")
    
    class Meta:
        ordering = ['min_amount']
    
    def __str__(self):
        return f"{self.get_name_display()} (${self.min_amount}+)"

class DonationGoal(models.Model):
    GOAL_STATUS = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
    ]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_amount = models.DecimalField(max_digits=10, decimal_places=2)
    current_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=GOAL_STATUS, default='active')
    image = models.ImageField(upload_to='donation_goals/', null=True, blank=True)
    
    @property
    def progress_percentage(self):
        if self.target_amount > 0:
            return min(100, (float(self.current_amount) / float(self.target_amount)) * 100)
        return 0
    
    @property
    def is_completed(self):
        return self.current_amount >= self.target_amount
    
    def update_progress(self, amount):
        self.current_amount += Decimal(str(amount))
        if self.is_completed and self.status == 'active':
            self.status = 'completed'
        self.save()
    
    def __str__(self):
        return f"{self.title} - ${self.current_amount}/${self.target_amount}"

class Donation(models.Model):
    DONATION_TYPES = [
        ('one_time', 'One-time Donation'),
        ('monthly', 'Monthly Recurring'),
        ('yearly', 'Yearly Recurring'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='donations')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donor_name = models.CharField(max_length=100, default="Anonymous")
    donor_email = models.EmailField(null=True, blank=True)
    donation_type = models.CharField(max_length=20, choices=DONATION_TYPES, default='one_time')
    is_recurring = models.BooleanField(default=False)
    next_payment_date = models.DateTimeField(null=True, blank=True)
    paypal_subscription_id = models.CharField(max_length=100, null=True, blank=True)
    donated_at = models.DateTimeField(auto_now_add=True)
    sponsor_tier = models.ForeignKey(SponsorTier, on_delete=models.SET_NULL, null=True, blank=True)
    donation_goal = models.ForeignKey(DonationGoal, on_delete=models.SET_NULL, null=True, blank=True)
    thank_you_sent = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        # Determine sponsor tier based on amount
        if not self.sponsor_tier:
            tier = SponsorTier.objects.filter(min_amount__lte=self.amount).order_by('-min_amount').first()
            if tier:
                self.sponsor_tier = tier
        
        # Update donation goal progress
        if self.donation_goal and not self.pk:  # Only for new donations
            self.donation_goal.update_progress(self.amount)
        
        # Update user profile if user is logged in
        if self.user and not self.pk:  # Only for new donations
            profile, created = UserProfile.objects.get_or_create(user=self.user)
            profile.total_donated += self.amount
            profile.update_tier()
            
            # Auto-fill donor info from user profile
            if not self.donor_name or self.donor_name == "Anonymous":
                self.donor_name = self.user.get_full_name() or self.user.username
            if not self.donor_email:
                self.donor_email = self.user.email
        
        super().save(*args, **kwargs)
        
        # Send thank you email
        if not self.thank_you_sent and self.donor_email:
            self.send_thank_you_email()
    
    def send_thank_you_email(self):
        from django.template.loader import render_to_string
        from django.core.mail import send_mail
        from django.utils.html import strip_tags
        
        try:
            # Prepare context for email template
            perks_html = ""
            if self.sponsor_tier and self.sponsor_tier.perks:
                perks_list = [perk.strip() for perk in self.sponsor_tier.perks.split('\n') if perk.strip()]
                perks_html = ''.join([f'<p style="margin: 5px 0;">• {perk}</p>' for perk in perks_list])
            
            context = {
                'donor_name': self.donor_name,
                'amount': self.amount,
                'donation_type': self.get_donation_type_display(),
                'is_recurring': self.is_recurring,
                'sponsor_tier': self.sponsor_tier,
                'donation_goal': self.donation_goal,
                'perks_html': perks_html,
            }
            
            # Render HTML email
            html_message = render_to_string('studio/emails/thank_you.html', context)
            
            # Create plain text version
            plain_message = f"""
Dear {self.donor_name},

Thank you so much for your generous ${self.amount} donation to Gaming Studio!

Your support helps us continue creating amazing games and building our community.

Donation Details:
- Amount: ${self.amount}
- Type: {self.get_donation_type_display()}
{'- Supporter Tier: ' + self.sponsor_tier.get_name_display() if self.sponsor_tier else ''}
{'- Supporting Goal: ' + self.donation_goal.title if self.donation_goal else ''}

{'This is a recurring donation that will automatically renew.' if self.is_recurring else ''}

You can view your impact and our progress at: https://gaming-studio.onrender.com/community

With gratitude,
The Gaming Studio Team
            """
            
            subject = f"Thank you for your {'recurring' if self.is_recurring else ''} ${self.amount} donation! 🎮"
            
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[self.donor_email],
                html_message=html_message,
                fail_silently=True,
            )
            
            self.thank_you_sent = True
            self.save(update_fields=['thank_you_sent'])
            print(f"✅ Thank you email sent to {self.donor_email}")
            
        except Exception as e:
            print(f"❌ Failed to send thank you email: {e}")

    def __str__(self):
        return f"{self.donor_name} - ${self.amount} ({'Recurring' if self.is_recurring else 'One-time'})"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"

# Achievement System
class Achievement(models.Model):
    ACHIEVEMENT_TYPES = [
        ('first_donation', 'First Donation'),
        ('loyal_supporter', 'Loyal Supporter'),
        ('big_spender', 'Big Spender'),
        ('level_up', 'Level Up'),
        ('community_hero', 'Community Hero'),
        ('early_supporter', 'Early Supporter'),
        ('monthly_donor', 'Monthly Donor'),
        ('game_enthusiast', 'Game Enthusiast'),
        ('social_butterfly', 'Social Butterfly'),
        ('veteran', 'Veteran Member'),
    ]
    
    type = models.CharField(max_length=50, choices=ACHIEVEMENT_TYPES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fas fa-trophy')
    color = models.CharField(max_length=7, default='#FFD700')  # Gold color
    experience_reward = models.IntegerField(default=50)
    is_rare = models.BooleanField(default=False)
    
    def __str__(self):
        return self.name

class UserAchievement(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_date = models.DateTimeField(auto_now_add=True)
    is_showcased = models.BooleanField(default=False)  # Whether user displays this on profile
    
    class Meta:
        unique_together = ['user', 'achievement']
    
    def __str__(self):
        return f"{self.user.username} - {self.achievement.name}"

# Gaming Activity Tracking
class UserActivity(models.Model):
    ACTIVITY_TYPES = [
        ('login', 'Login'),
        ('donation', 'Donation'),
        ('comment', 'Comment'),
        ('profile_update', 'Profile Update'),
        ('achievement_earned', 'Achievement Earned'),
        ('level_up', 'Level Up'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='activities')
    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=200)
    timestamp = models.DateTimeField(auto_now_add=True)
    experience_gained = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-timestamp']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_activity_type_display()}"

# Enhanced Social Features
class UserFollow(models.Model):
    """User following system"""
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following_relationships')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='follower_relationships')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['follower', 'following']
    
    def __str__(self):
        return f"{self.follower.username} follows {self.following.username}"

class FeaturedAchievement(models.Model):
    """User's featured achievements on profile"""
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    display_order = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user_profile', 'achievement']
        ordering = ['display_order']
    
    def __str__(self):
        return f"{self.user_profile.user.username} features {self.achievement.name}"

# Gaming Statistics and Records
class GameSession(models.Model):
    """Track user gaming sessions"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_sessions')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='play_sessions')
    start_time = models.DateTimeField(auto_now_add=True)
    duration_minutes = models.PositiveIntegerField(help_text="Session duration in minutes")
    experience_gained = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} played {self.game.title} for {self.duration_minutes}min"

# Game Collections and Wishlists
class GameCollection(models.Model):
    """User-created game collections"""
    COLLECTION_TYPES = [
        ('personal', 'Personal Collection'),
        ('wishlist', 'Wishlist'),
        ('favorites', 'Favorites'),
        ('completed', 'Completed Games'),
        ('playing', 'Currently Playing'),
        ('custom', 'Custom Collection'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_collections')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    collection_type = models.CharField(max_length=20, choices=COLLECTION_TYPES, default='custom')
    games = models.ManyToManyField(Game, related_name='collections', blank=True)
    is_public = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'name']
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.user.username}'s {self.name}"

class GameWishlist(models.Model):
    """Simple wishlist for games"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist_items')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='wishlist_entries')
    added_at = models.DateTimeField(auto_now_add=True)
    priority = models.IntegerField(choices=[
        (1, 'Low'),
        (2, 'Medium'),
        (3, 'High'),
        (4, 'Must Have'),
    ], default=2)
    
    class Meta:
        unique_together = ['user', 'game']
        ordering = ['-priority', '-added_at']
    
    def __str__(self):
        return f"{self.user.username} wants {self.game.title}"

# Enhanced Game Analytics
class GameAnalytics(models.Model):
    """Daily analytics for games"""
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='analytics')
    date = models.DateField(auto_now_add=True)
    views = models.IntegerField(default=0)
    downloads = models.IntegerField(default=0)
    shares = models.IntegerField(default=0)
    wishlist_adds = models.IntegerField(default=0)
    
    class Meta:
        unique_together = ['game', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.game.title} analytics for {self.date}"

# Game Categories and Tags
class GameCategory(models.Model):
    """Hierarchical game categories"""
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subcategories')
    icon = models.CharField(max_length=50, blank=True, help_text="Font Awesome icon class")
    color = models.CharField(max_length=7, default='#6366f1', help_text="Hex color code")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['order', 'name']
        verbose_name_plural = 'Game Categories'
    
    def __str__(self):
        return self.name
    
    def get_games_count(self):
        return self.games.filter(status='released').count()

class GameTag(models.Model):
    """Flexible tagging system for games"""
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    games = models.ManyToManyField(Game, related_name='game_tags', blank=True)
    usage_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return f"#{self.name} ({self.usage_count})"

# Game Download and Distribution
class GameDownload(models.Model):
    """Track game downloads"""
    PLATFORM_CHOICES = [
        ('windows', 'Windows'),
        ('mac', 'macOS'),
        ('linux', 'Linux'),
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('web', 'Web Browser'),
    ]
    
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='downloads')
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    version = models.CharField(max_length=20, default='1.0.0')
    file_url = models.URLField(max_length=500, blank=True)
    file_size_mb = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    download_count = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['game', 'platform', 'version']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.game.title} - {self.get_platform_display()} v{self.version}"
    achievements_unlocked = models.ManyToManyField(Achievement, blank=True)
    
    def __str__(self):
        return f"{self.user.username} played {self.game.title} for {self.duration_minutes}min"

class UserGameStats(models.Model):
    """Detailed gaming statistics for each user-game combination"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_stats')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='user_stats')
    total_playtime_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sessions_count = models.PositiveIntegerField(default=0)
    achievements_earned = models.PositiveIntegerField(default=0)
    favorite_game = models.BooleanField(default=False)
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)], null=True, blank=True)
    last_played = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'game']
    
    def __str__(self):
        return f"{self.user.username} - {self.game.title} Stats"

# User Reviews and Community Features
class GameReview(models.Model):
    """User reviews for games"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='game_reviews')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='reviews')
    rating = models.PositiveIntegerField(choices=[(i, i) for i in range(1, 6)])
    title = models.CharField(max_length=200)
    content = models.TextField()
    likes_count = models.PositiveIntegerField(default=0)
    is_recommended = models.BooleanField(default=True)
    playtime_hours = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'game']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.username}'s review of {self.game.title}"

class ReviewLike(models.Model):
    """Track likes on game reviews"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    review = models.ForeignKey(GameReview, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'review']
    
    def __str__(self):
        return f"{self.user.username} likes {self.review.title}"

# Enhanced Achievement System
class AchievementCategory(models.Model):
    """Categories for organizing achievements"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, default='fas fa-trophy')
    color = models.CharField(max_length=7, default='#FFD700')
    
    class Meta:
        verbose_name_plural = "Achievement Categories"
    
    def __str__(self):
        return self.name

# Update Achievement model to include category
# This will be added in a migration later
class MilestoneAchievement(models.Model):
    """Special milestone achievements with progression tracking"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField()
    target_value = models.PositiveIntegerField()
    current_value = models.PositiveIntegerField(default=0)
    achievement_type = models.CharField(max_length=50, choices=[
        ('donations', 'Total Donations'),
        ('playtime', 'Total Playtime'),
        ('achievements', 'Achievements Earned'),
        ('social', 'Social Interactions'),
        ('reviews', 'Reviews Written'),
    ])
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    reward_experience = models.PositiveIntegerField(default=100)
    
    @property
    def progress_percentage(self):
        if self.target_value > 0:
            return min(100, (self.current_value / self.target_value) * 100)
        return 0
    
    def check_completion(self):
        if not self.is_completed and self.current_value >= self.target_value:
            self.is_completed = True
            self.completed_at = timezone.now()
            # Award experience to user
            profile = UserProfile.objects.get(user=self.user)
            profile.add_experience(self.reward_experience)
            self.save()
            return True
        return False
    
    def __str__(self):
        return f"{self.user.username} - {self.title} ({self.current_value}/{self.target_value})"