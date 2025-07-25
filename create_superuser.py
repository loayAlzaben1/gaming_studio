#!/usr/bin/env python3
"""
Create a superuser for Gaming Studio Django application
"""
import os
import sys
import django
from pathlib import Path

# Add the project directory to Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaming_studio.settings')

def create_custom_superuser():
    """Create a superuser with custom credentials"""
    print("🎮 Gaming Studio - Create Superuser")
    print("=" * 40)
    
    # Setup Django
    django.setup()
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        # Get user input
        print("\nEnter superuser details:")
        username = input("Username: ").strip()
        if not username:
            username = "admin"
            print(f"Using default username: {username}")
        
        email = input("Email: ").strip()
        if not email:
            email = "admin@gamingstudio.com"
            print(f"Using default email: {email}")
        
        password = input("Password: ").strip()
        if not password:
            password = "admin123"
            print(f"Using default password: {password}")
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            print(f"❌ User '{username}' already exists!")
            overwrite = input("Do you want to delete and recreate? (y/N): ").strip().lower()
            if overwrite == 'y':
                User.objects.filter(username=username).delete()
                print(f"✅ Deleted existing user '{username}'")
            else:
                print("Operation cancelled.")
                return
        
        # Create superuser
        user = User.objects.create_superuser(
            username=username,
            email=email,
            password=password
        )
        
        print("\n🎉 Superuser created successfully!")
        print("=" * 40)
        print(f"Username: {username}")
        print(f"Email: {email}")
        print(f"Password: {password}")
        print(f"🔗 Admin URL: http://127.0.0.1:8000/admin/")
        print("=" * 40)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user.")
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")

def create_default_superuser():
    """Create a superuser with default credentials (for automation)"""
    print("Creating default superuser...")
    
    # Setup Django
    django.setup()
    
    from django.contrib.auth import get_user_model
    User = get_user_model()
    
    try:
        if not User.objects.filter(is_superuser=True).exists():
            user = User.objects.create_superuser(
                username='admin',
                email='admin@gamingstudio.com',
                password='admin123'
            )
            print("✅ Default superuser created!")
            print("   Username: admin")
            print("   Password: admin123")
            print("   🔗 Admin URL: http://127.0.0.1:8000/admin/")
        else:
            print("✅ Superuser already exists")
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Create a superuser for Gaming Studio')
    parser.add_argument('--default', action='store_true', 
                       help='Create default superuser (admin/admin123)')
    parser.add_argument('--custom', action='store_true', 
                       help='Create superuser with custom credentials')
    
    args = parser.parse_args()
    
    if args.default:
        create_default_superuser()
    elif args.custom:
        create_custom_superuser()
    else:
        # Interactive mode - ask user what they want
        print("🎮 Gaming Studio - Superuser Creation")
        print("=" * 40)
        print("1. Create default superuser (admin/admin123)")
        print("2. Create custom superuser")
        print("3. Exit")
        
        while True:
            choice = input("\nSelect option (1-3): ").strip()
            if choice == '1':
                create_default_superuser()
                break
            elif choice == '2':
                create_custom_superuser()
                break
            elif choice == '3':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1, 2, or 3.")
