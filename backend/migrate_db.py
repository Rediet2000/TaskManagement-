from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate():
    # Force use of internal docker service name if running inside container, but we are running from host
    # So we need to use localhost and port 5432 which is mapped in docker-compose
    # The config has: postgresql://postgres:postgres@localhost/taskmanagement
    
    print(f"Connecting to database...")
    engine = create_engine(settings.DATABASE_URL)
    
    with engine.connect() as conn:
        print("Checking for missing columns...")
        
        # Add rating column
        try:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN rating INTEGER NULL"))
            print("Added 'rating' column.")
        except Exception as e:
            print(f"Skipping 'rating' (probably exists): {e}")
            
        # Add rating_comment column
        try:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN rating_comment TEXT NULL"))
            print("Added 'rating_comment' column.")
        except Exception as e:
            print(f"Skipping 'rating_comment' (probably exists): {e}")

        # Add completed_at column
        try:
            conn.execute(text("ALTER TABLE tasks ADD COLUMN completed_at TIMESTAMP WITH TIME ZONE NULL"))
            print("Added 'completed_at' column.")
        except Exception as e:
            print(f"Skipping 'completed_at' (probably exists): {e}")
            
        conn.commit()
        print("Migration completed.")

if __name__ == "__main__":
    migrate()
