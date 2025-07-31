#!/usr/bin/env python
"""
Database Setup Script
Creates all required tables if they don't exist
"""
import os
import django
import sys

# Add the project directory to the path
sys.path.append('/opt/render/project/src')

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaming_studio.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.conf import settings

def setup_database():
    """Set up the database tables"""
    
    print("🔧 Setting up database tables...")
    
    try:
        # Run migrations
        print("📋 Running migrations...")
        call_command('migrate', verbosity=2)
        print("✅ Database migrations completed!")
        
        # Check if tables exist
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            print(f"📊 Database tables: {tables}")
            
        return True
        
    except Exception as e:
        print(f"❌ Database setup error: {e}")
        return False

if __name__ == '__main__':
    setup_database()
