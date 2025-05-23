from django.db import models

class Game(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    platform = models.CharField(max_length=50)
    release_date = models.DateField()
    cover_image = models.ImageField(upload_to='games/')
    trailer_link = models.URLField()

    def __str__(self):
        return self.title

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class TeamMember(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    bio = models.TextField()
    photo = models.ImageField(upload_to='team/')

    def __str__(self):
        return self.name

class Donation(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    donor_name = models.CharField(max_length=100)
    donated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.donor_name} - ${self.amount}"