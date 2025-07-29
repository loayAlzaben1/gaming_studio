#!/usr/bin/env python
"""
ULTRA MINIMAL FIX - Only create what's absolutely necessary
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaming_studio.settings')
django.setup()

from django.db import connection

print("🔥 ULTRA MINIMAL FIX STARTING")

# Only create studio_game table - nothing else
try:
    with connection.cursor() as cursor:
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS studio_game (
            id INTEGER PRIMARY KEY,
            title TEXT DEFAULT 'RTS Game',
            description TEXT DEFAULT 'A game',
            cover_image TEXT DEFAULT '',
            is_featured INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        # Insert one game
        cursor.execute("DELETE FROM studio_game;")  # Clear first
        cursor.execute("""
        INSERT INTO studio_game (id, title, description, is_featured) 
        VALUES (1, 'RTS Strategy Game', 'Epic gaming experience', 1);
        """)
        
    print("✅ ULTRA MINIMAL TABLE CREATED")
    
    # Verify
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM studio_game;")
        count = cursor.fetchone()[0]
        print(f"✅ Games in database: {count}")
        
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

print("🎉 ULTRA MINIMAL FIX COMPLETE!")
