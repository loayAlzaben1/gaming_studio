#!/usr/bin/env python
"""
Emergency Database Migration Script
Fixes: no such table: studio_game error after authentication removal
"""
import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaming_studio.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def fix_database():
    """Fix database tables after authentication removal"""
    
    print("🔧 EMERGENCY DATABASE FIX - Fixing studio_game table")
    
    try:
        # Run migrations to create missing tables
        print("📊 Running database migrations...")
        call_command('makemigrations', verbosity=2)
        call_command('migrate', verbosity=2)
        
        # Verify tables exist
        print("✅ Verifying database tables...")
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            
        print(f"📋 Found {len(tables)} tables:")
        for table in tables:
            print(f"   - {table[0]}")
            
        # Check if studio_game exists
        studio_tables = [t[0] for t in tables if 'studio_' in t[0]]
        if 'studio_game' in studio_tables:
            print("✅ studio_game table exists!")
        else:
            print("❌ studio_game table missing - creating...")
            call_command('migrate', 'studio', verbosity=2)
            
        print("🎯 Database fix complete!")
        
    except Exception as e:
        print(f"❌ Database fix error: {e}")

if __name__ == '__main__':
    fix_database()
