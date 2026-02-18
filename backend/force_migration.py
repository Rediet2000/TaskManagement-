import psycopg2
from app.core.config import settings
import sys

def force_migrate():
    print(f"Connecting to database at {settings.DATABASE_URL}...")
    
    # Parse the URL manually to get connection params
    # postgresql://postgres:postgres@db:5432/taskmanagement
    import re
    match = re.search(r"postgresql://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)", settings.DATABASE_URL)
    if not match:
        print("Could not parse DATABASE_URL")
        sys.exit(1)
        
    user, password, host, port, dbname = match.groups()
    
    try:
        conn = psycopg2.connect(
            dbname=dbname,
            user=user,
            password=password,
            host=host,
            port=port
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        print("Connected. Attempting to add columns...")
        
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN rating INTEGER NULL;")
            print("SUCCESS: Added 'rating' column.")
        except psycopg2.errors.DuplicateColumn:
            print("INFO: 'rating' column already exists.")
        except Exception as e:
            print(f"ERROR adding 'rating': {e}")
            
        try:
            cursor.execute("ALTER TABLE tasks ADD COLUMN rating_comment TEXT NULL;")
            print("SUCCESS: Added 'rating_comment' column.")
        except psycopg2.errors.DuplicateColumn:
            print("INFO: 'rating_comment' column already exists.")
        except Exception as e:
            print(f"ERROR adding 'rating_comment': {e}")
            
        cursor.close()
        conn.close()
        print("Migration finished.")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    force_migrate()
