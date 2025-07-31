#!/usr/bin/env python
"""
Emergency database setup script for Render deployment
This creates the essential tables if migrations fail
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'gaming_studio.settings')
django.setup()

from django.db import connection, transaction
from django.apps import apps

def create_essential_tables():
    """Create essential tables manually if migrations fail"""
    try:
        print("==> Starting emergency database setup...")
        print(f"Database file exists: {os.path.exists('db.sqlite3')}")
        
        with connection.cursor() as cursor:
            # Check if studio_game table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='studio_game';")
            if cursor.fetchone():
                print("studio_game table already exists")
                return True
            
            print("Creating studio_game table manually...")
            print("Executing CREATE TABLE statement...")
            
            # Create studio_game table with essential fields
            create_game_table_sql = """
            CREATE TABLE "studio_game" (
                "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                "title" varchar(200) NOT NULL,
                "description" text NOT NULL,
                "short_description" varchar(500) NOT NULL,
                "genre" varchar(100) NOT NULL,
                "platform" varchar(100) NOT NULL,
                "release_date" date,
                "status" varchar(20) NOT NULL,
                "cover_image" varchar(100),
                "trailer_link" varchar(200),
                "tags" varchar(500),
                "age_rating" varchar(10) NOT NULL,
                "min_players" integer,
                "max_players" integer,
                "estimated_playtime" integer,
                "is_featured" bool NOT NULL,
                "featured_order" integer,
                "average_rating" decimal NOT NULL,
                "total_reviews" integer NOT NULL,
                "play_count" integer NOT NULL,
                "wishlist_count" integer NOT NULL,
                "download_count" integer NOT NULL,
                "created_at" datetime NOT NULL,
                "updated_at" datetime NOT NULL
            );
            """
            
            cursor.execute(create_game_table_sql)
            print("studio_game table created successfully")
            
            # Create other essential tables if needed
            essential_tables = [
                ("studio_donation", """
                CREATE TABLE "studio_donation" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "donor_name" varchar(100) NOT NULL,
                    "donor_email" varchar(254),
                    "amount" decimal NOT NULL,
                    "donated_at" datetime NOT NULL,
                    "donation_type" varchar(20) NOT NULL,
                    "is_recurring" bool NOT NULL,
                    "thank_you_sent" bool NOT NULL
                );
                """),
                ("studio_userprofile", """
                CREATE TABLE "studio_userprofile" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "user_id" bigint NOT NULL UNIQUE,
                    "bio" text NOT NULL,
                    "avatar" varchar(100),
                    "join_date" datetime NOT NULL,
                    "account_level" integer NOT NULL,
                    "experience_points" integer NOT NULL,
                    "total_donated" decimal NOT NULL,
                    "is_premium" bool NOT NULL
                );
                """),
                ("studio_donationgoal", """
                CREATE TABLE "studio_donationgoal" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "title" varchar(200) NOT NULL,
                    "description" text NOT NULL,
                    "target_amount" decimal NOT NULL,
                    "current_amount" decimal NOT NULL,
                    "is_active" bool NOT NULL,
                    "created_at" datetime NOT NULL,
                    "updated_at" datetime NOT NULL
                );
                """),
                ("studio_teammember", """
                CREATE TABLE "studio_teammember" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "name" varchar(100) NOT NULL,
                    "role" varchar(100) NOT NULL,
                    "bio" text NOT NULL,
                    "photo" varchar(100),
                    "social_link" varchar(200),
                    "join_date" datetime NOT NULL
                );
                """),
                ("studio_sponsortier", """
                CREATE TABLE "studio_sponsortier" (
                    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                    "name" varchar(50) NOT NULL,
                    "icon" varchar(50),
                    "color" varchar(20),
                    "min_amount" decimal NOT NULL,
                    "created_at" datetime NOT NULL,
                    "updated_at" datetime NOT NULL
                );
                """)
            ]
            
            for table_name, create_sql in essential_tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}';")
                if not cursor.fetchone():
                    cursor.execute(create_sql)
                    print(f"{table_name} table created")
                else:
                    print(f"{table_name} table already exists")
            
            return True
            
    except Exception as e:
        print(f"Error creating tables manually: {e}")
        return False

if __name__ == "__main__":
    success = create_essential_tables()
    if success:
        print("Emergency database setup completed successfully!")
        sys.exit(0)
    else:
        print("Emergency database setup failed!")
        sys.exit(1)
