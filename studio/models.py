from django.db import models

class Game(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    platform = models.CharField(max_length=100)
    release_date = models.DateField()
    cover_image = models.ImageField(upload_to='game_covers/', null=True, blank=True)
    trailer_link = models.URLField(max_length=200, null=True, blank=True)
    photos = models.ManyToManyField('Photo', related_name='games', blank=True)
    videos = models.ManyToManyField('Video', related_name='games', blank=True)
    is_featured = models.BooleanField(default=False, help_text="Designates whether this game is featured on the home page.")

    def __str__(self):
        return self.title

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

class Donation(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donor_name = models.CharField(max_length=100, default="Anonymous")
    donated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor_name} - ${self.amount}"

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.email}"