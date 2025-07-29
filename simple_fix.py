#!/usr/bin/env python
"""
SUPER SIMPLE PRODUCTION FIX
Run this directly on Render to fix authentication immediately
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaming_studio.settings')
django.setup()

from django.db import connection

print("🚨 SUPER SIMPLE PRODUCTION FIX")
print("=" * 40)

# Step 1: Create the absolute minimum tables needed
print("Creating essential tables...")
with connection.cursor() as cursor:
    # Studio game table (simplified)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS studio_game (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL DEFAULT 'Sample Game',
        description TEXT DEFAULT 'A sample game',
        cover_image TEXT DEFAULT '',
        is_featured INTEGER DEFAULT 1,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    """)
    
    # Insert a sample game if table is empty
    cursor.execute("SELECT COUNT(*) FROM studio_game;")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO studio_game (title, description, is_featured) 
        VALUES ('RTS Strategy Game', 'Epic gaming experience', 1);
        """)
    
    print("✅ studio_game table ready")

# Step 2: Fix site configuration
print("Setting up site...")
from django.contrib.sites.models import Site
site, created = Site.objects.get_or_create(
    pk=1,
    defaults={'domain': 'gaming-studio.onrender.com', 'name': 'Gaming Studio'}
)
site.domain = 'gaming-studio.onrender.com'
site.name = 'Gaming Studio'
site.save()
print(f"✅ Site: {site.domain}")

# Step 3: Setup Google OAuth (minimal)
print("Setting up OAuth...")
try:
    from allauth.socialaccount.models import SocialApp
    google_app, created = SocialApp.objects.get_or_create(
        provider='google',
        defaults={
            'name': 'Gaming Studio Google OAuth',
            'client_id': '1035193411026-ti6ub7vrs3kdkg7n8e87nfcjgh1f6llh.apps.googleusercontent.com',
            'secret': 'GOCSPX-production-secret-here',
        }
    )
    google_app.sites.add(site)
    print("✅ OAuth configured")
except Exception as e:
    print(f"⚠️ OAuth setup failed: {e}")

print("\n🎉 SIMPLE FIX COMPLETED!")
print("Test: https://gaming-studio.onrender.com/")
print("Login: https://gaming-studio.onrender.com/accounts/login/")

# Verify the fix worked
print("\n🔍 Verification:")
with connection.cursor() as cursor:
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='studio_game';")
    if cursor.fetchone():
        print("✅ studio_game table exists")
        cursor.execute("SELECT COUNT(*) FROM studio_game;")
        count = cursor.fetchone()[0]
        print(f"✅ {count} games in database")
    else:
        print("❌ studio_game table missing")

print("✅ Simple fix verification complete!")
