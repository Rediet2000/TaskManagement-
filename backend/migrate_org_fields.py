import psycopg2
from app.core.config import settings
import sys
import re

def migrate_org_fields():
    print(f"Connecting to database at {settings.DATABASE_URL}...")
    
    # Parse the URL manually to get connection params
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
        
        print("Connected. Attempting to add Organization fields...")
        
        # List of new fields to add
        new_fields = [
            ("industry", "VARCHAR"),
            ("address", "VARCHAR"),
            ("timezone", "VARCHAR DEFAULT 'UTC'"),
            ("default_language", "VARCHAR DEFAULT 'en'"),
            ("contact_phone", "VARCHAR"),
            ("contact_email", "VARCHAR")
        ]

        for field_name, field_type in new_fields:
            try:
                # check if column exists
                cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='organizations' AND column_name='{field_name}';")
                if cursor.fetchone():
                    print(f"INFO: '{field_name}' column already exists.")
                    continue

                cursor.execute(f"ALTER TABLE organizations ADD COLUMN {field_name} {field_type};")
                print(f"SUCCESS: Added '{field_name}' column.")
            except Exception as e:
                print(f"ERROR adding '{field_name}': {e}")
            
        cursor.close()
        conn.close()
        print("Migration finished.")
        
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    migrate_org_fields()
