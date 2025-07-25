# Generated by Django 5.2.1 on 2025-07-26 19:29

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('studio', '0012_auto_20250726_2228'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='GameAnalytics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(auto_now_add=True)),
                ('views', models.IntegerField(default=0)),
                ('downloads', models.IntegerField(default=0)),
                ('shares', models.IntegerField(default=0)),
                ('wishlist_adds', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['-date'],
            },
        ),
        migrations.CreateModel(
            name='GameCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('description', models.TextField(blank=True)),
                ('icon', models.CharField(blank=True, help_text='Font Awesome icon class', max_length=50)),
                ('color', models.CharField(default='#6366f1', help_text='Hex color code', max_length=7)),
                ('is_active', models.BooleanField(default=True)),
                ('order', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name_plural': 'Game Categories',
                'ordering': ['order', 'name'],
            },
        ),
        migrations.CreateModel(
            name='GameCollection',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('description', models.TextField(blank=True)),
                ('collection_type', models.CharField(choices=[('personal', 'Personal Collection'), ('wishlist', 'Wishlist'), ('favorites', 'Favorites'), ('completed', 'Completed Games'), ('playing', 'Currently Playing'), ('custom', 'Custom Collection')], default='custom', max_length=20)),
                ('is_public', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-updated_at'],
            },
        ),
        migrations.CreateModel(
            name='GameDownload',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('platform', models.CharField(choices=[('windows', 'Windows'), ('mac', 'macOS'), ('linux', 'Linux'), ('android', 'Android'), ('ios', 'iOS'), ('web', 'Web Browser')], max_length=20)),
                ('version', models.CharField(default='1.0.0', max_length=20)),
                ('file_url', models.URLField(blank=True, max_length=500)),
                ('file_size_mb', models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True)),
                ('download_count', models.IntegerField(default=0)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='GameTag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('slug', models.SlugField(unique=True)),
                ('usage_count', models.IntegerField(default=0)),
            ],
            options={
                'ordering': ['-usage_count', 'name'],
            },
        ),
        migrations.CreateModel(
            name='GameWishlist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('added_at', models.DateTimeField(auto_now_add=True)),
                ('priority', models.IntegerField(choices=[(1, 'Low'), (2, 'Medium'), (3, 'High'), (4, 'Must Have')], default=2)),
            ],
            options={
                'ordering': ['-priority', '-added_at'],
            },
        ),
        migrations.AlterModelOptions(
            name='game',
            options={'ordering': ['-created_at']},
        ),
        migrations.RemoveField(
            model_name='gamesession',
            name='achievements_unlocked',
        ),
        migrations.AddField(
            model_name='game',
            name='age_rating',
            field=models.CharField(blank=True, choices=[('E', 'Everyone'), ('E10+', 'Everyone 10+'), ('T', 'Teen'), ('M', 'Mature 17+'), ('AO', 'Adults Only'), ('RP', 'Rating Pending')], default='E', max_length=10),
        ),
        migrations.AddField(
            model_name='game',
            name='average_rating',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=3),
        ),
        migrations.AddField(
            model_name='game',
            name='created_at',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='game',
            name='download_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='game',
            name='estimated_playtime',
            field=models.CharField(blank=True, help_text="e.g., '2-4 hours', '50+ hours'", max_length=50),
        ),
        migrations.AddField(
            model_name='game',
            name='featured_order',
            field=models.IntegerField(default=0, help_text='Order for featured games (0 = not featured)'),
        ),
        migrations.AddField(
            model_name='game',
            name='genre',
            field=models.CharField(choices=[('action', 'Action'), ('adventure', 'Adventure'), ('rpg', 'RPG'), ('strategy', 'Strategy'), ('simulation', 'Simulation'), ('puzzle', 'Puzzle'), ('horror', 'Horror'), ('racing', 'Racing'), ('sports', 'Sports'), ('fighting', 'Fighting'), ('shooter', 'Shooter'), ('platformer', 'Platformer'), ('mmorpg', 'MMORPG'), ('indie', 'Indie'), ('casual', 'Casual')], default='action', max_length=50),
        ),
        migrations.AddField(
            model_name='game',
            name='max_players',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='game',
            name='min_players',
            field=models.IntegerField(default=1),
        ),
        migrations.AddField(
            model_name='game',
            name='play_count',
            field=models.IntegerField(default=0, help_text='Number of times this game has been played'),
        ),
        migrations.AddField(
            model_name='game',
            name='short_description',
            field=models.CharField(blank=True, help_text='Brief description for cards and previews', max_length=300),
        ),
        migrations.AddField(
            model_name='game',
            name='status',
            field=models.CharField(choices=[('development', 'In Development'), ('alpha', 'Alpha'), ('beta', 'Beta'), ('released', 'Released'), ('coming_soon', 'Coming Soon'), ('early_access', 'Early Access'), ('cancelled', 'Cancelled')], default='development', max_length=20),
        ),
        migrations.AddField(
            model_name='game',
            name='tags',
            field=models.CharField(blank=True, help_text='Comma-separated tags for better discovery', max_length=300),
        ),
        migrations.AddField(
            model_name='game',
            name='total_reviews',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='game',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='game',
            name='wishlist_count',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='game',
            name='platform',
            field=models.CharField(choices=[('pc', 'PC'), ('playstation', 'PlayStation'), ('xbox', 'Xbox'), ('nintendo', 'Nintendo Switch'), ('mobile', 'Mobile'), ('web', 'Web Browser'), ('vr', 'Virtual Reality'), ('multiple', 'Multi-Platform')], default='pc', max_length=100),
        ),
        migrations.AddIndex(
            model_name='game',
            index=models.Index(fields=['status'], name='studio_game_status_622fe1_idx'),
        ),
        migrations.AddIndex(
            model_name='game',
            index=models.Index(fields=['genre'], name='studio_game_genre_8937e7_idx'),
        ),
        migrations.AddIndex(
            model_name='game',
            index=models.Index(fields=['platform'], name='studio_game_platfor_7bd5d5_idx'),
        ),
        migrations.AddIndex(
            model_name='game',
            index=models.Index(fields=['-average_rating'], name='studio_game_average_428955_idx'),
        ),
        migrations.AddIndex(
            model_name='game',
            index=models.Index(fields=['-featured_order'], name='studio_game_feature_b3079f_idx'),
        ),
        migrations.AddField(
            model_name='gameanalytics',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='analytics', to='studio.game'),
        ),
        migrations.AddField(
            model_name='gamecategory',
            name='parent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='subcategories', to='studio.gamecategory'),
        ),
        migrations.AddField(
            model_name='gamecollection',
            name='games',
            field=models.ManyToManyField(blank=True, related_name='collections', to='studio.game'),
        ),
        migrations.AddField(
            model_name='gamecollection',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='game_collections', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='gamedownload',
            name='achievements_unlocked',
            field=models.ManyToManyField(blank=True, to='studio.achievement'),
        ),
        migrations.AddField(
            model_name='gamedownload',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='downloads', to='studio.game'),
        ),
        migrations.AddField(
            model_name='gametag',
            name='games',
            field=models.ManyToManyField(blank=True, related_name='game_tags', to='studio.game'),
        ),
        migrations.AddField(
            model_name='gamewishlist',
            name='game',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_entries', to='studio.game'),
        ),
        migrations.AddField(
            model_name='gamewishlist',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='wishlist_items', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterUniqueTogether(
            name='gameanalytics',
            unique_together={('game', 'date')},
        ),
        migrations.AlterUniqueTogether(
            name='gamecollection',
            unique_together={('user', 'name')},
        ),
        migrations.AlterUniqueTogether(
            name='gamedownload',
            unique_together={('game', 'platform', 'version')},
        ),
        migrations.AlterUniqueTogether(
            name='gamewishlist',
            unique_together={('user', 'game')},
        ),
    ]
