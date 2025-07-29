from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Ultra minimal fix - only create studio_game table'

    def handle(self, *args, **options):
        self.stdout.write("🔥 ULTRA MINIMAL FIX")
        
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
                
                cursor.execute("DELETE FROM studio_game;")
                cursor.execute("""
                INSERT INTO studio_game (id, title, description, is_featured) 
                VALUES (1, 'RTS Strategy Game', 'Epic gaming experience', 1);
                """)
                
                cursor.execute("SELECT COUNT(*) FROM studio_game;")
                count = cursor.fetchone()[0]
                
            self.stdout.write(self.style.SUCCESS(f"✅ Created studio_game table with {count} games"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"❌ Error: {e}"))
