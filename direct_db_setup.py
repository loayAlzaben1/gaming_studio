#!/usr/bin/env python
"""
Direct database table creation for Render deployment
"""
import os
import sys
import sqlite3

def create_game_table():
    """Create studio_game table directly using sqlite3"""
    try:
        # Connect to database
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        
        # Check if table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='studio_game';")
        if cursor.fetchone():
            print("studio_game table already exists")
            conn.close()
            return True
        
        print("Creating studio_game table...")
        
        # Create the table with minimal required fields
        cursor.execute("""
        CREATE TABLE studio_game (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL DEFAULT '',
            description TEXT NOT NULL DEFAULT '',
            short_description VARCHAR(500) NOT NULL DEFAULT '',
            genre VARCHAR(100) NOT NULL DEFAULT 'Action',
            platform VARCHAR(100) NOT NULL DEFAULT 'PC',
            release_date DATE,
            status VARCHAR(20) NOT NULL DEFAULT 'development',
            cover_image VARCHAR(100),
            trailer_link VARCHAR(200),
            tags VARCHAR(500) DEFAULT '',
            age_rating VARCHAR(10) NOT NULL DEFAULT 'E',
            min_players INTEGER DEFAULT 1,
            max_players INTEGER DEFAULT 1,
            estimated_playtime INTEGER DEFAULT 60,
            is_featured BOOLEAN NOT NULL DEFAULT 0,
            featured_order INTEGER,
            average_rating DECIMAL NOT NULL DEFAULT 0.0,
            total_reviews INTEGER NOT NULL DEFAULT 0,
            play_count INTEGER NOT NULL DEFAULT 0,
            wishlist_count INTEGER NOT NULL DEFAULT 0,
            download_count INTEGER NOT NULL DEFAULT 0,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        """)
        
        conn.commit()
        conn.close()
        print("studio_game table created successfully!")
        return True
        
    except Exception as e:
        print(f"Error creating studio_game table: {e}")
        return False

if __name__ == "__main__":
    if create_game_table():
        print("Database setup completed!")
        sys.exit(0)
    else:
        print("Database setup failed!")
        sys.exit(1)
