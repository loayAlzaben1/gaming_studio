#!/usr/bin/env python3
"""
Deployment script for Gaming Studio Django application
Handles database migrations and static file collection before server start
"""
import os
import sys
import subprocess
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaming_studio.settings')

def run_command(command, description):
    """Run a command and handle errors gracefully"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error in {description}: {e}")
        if e.stderr:
            print(f"Error output: {e.stderr}")
        return False

def create_superuser():
    """Create a superuser if one doesn't exist"""
    print("Checking for superuser...")
    try:
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        if not User.objects.filter(is_superuser=True).exists():
            print("Creating superuser...")
            # Create superuser with default credentials
            User.objects.create_superuser(
                username='admin',
                email='admin@gamingstudio.com',
                password='admin123'
            )
            print("✅ Superuser created successfully!")
            print("   Username: admin")
            print("   Email: admin@gamingstudio.com")
            print("   Password: admin123")
            print("   🔗 Access admin at: http://127.0.0.1:8000/admin/")
        else:
            print("✅ Superuser already exists")
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")

def deploy():
    """Run deployment steps"""
    print("🚀 Starting deployment process...")
    
    # Setup Django
    django.setup()
    
    # Run migrations with syncdb to create missing tables
    print("📊 Running database migrations with syncdb...")
    if not run_command("python manage.py migrate --run-syncdb --noinput", "Database migrations with syncdb"):
        print("Migration with syncdb failed, trying regular migration...")
        if not run_command("python manage.py migrate --noinput", "Regular database migrations"):
            print("❌ Both migration attempts failed, but continuing...")
    
    # Verify database tables
    print("✅ Verifying database setup...")
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = [row[0] for row in cursor.fetchall()]
            studio_tables = [t for t in tables if 'studio_' in t]
            print(f"📋 Found {len(tables)} total tables, {len(studio_tables)} studio tables")
            if 'studio_game' in tables:
                print("✅ studio_game table exists!")
            else:
                print("❌ studio_game table missing!")
    except Exception as e:
        print(f"❌ Database verification error: {e}")
    
    # Collect static files
    if not run_command("python manage.py collectstatic --noinput --clear", "Static files collection"):
        print("Static files collection failed, but continuing...")
    
    # Create superuser
    create_superuser()
    
    print("🎯 Deployment process completed!")

if __name__ == "__main__":
    deploy()
