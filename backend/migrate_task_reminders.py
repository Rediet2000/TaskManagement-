import psycopg2
import os

def migrate():
    # Use environment variables if available, otherwise default to docker-compose values
    host = "localhost" # Assuming local dev since I'm running python commands on windows
    dbname = "taskmanagement"
    user = "postgres"
    password = "postgres"
    port = "5432"

    try:
        conn = psycopg2.connect(
            host=host,
            database=dbname,
            user=user,
            password=password,
            port=port
        )
        cur = conn.cursor()
        
        print(f"Checking if due_reminder_sent column exists in tasks table...")
        cur.execute("""
            SELECT count(*) 
            FROM information_schema.columns 
            WHERE table_name='tasks' AND column_name='due_reminder_sent';
        """)
        exists = cur.fetchone()[0] > 0
        
        if not exists:
            print("Adding due_reminder_sent column to tasks table...")
            cur.execute("ALTER TABLE tasks ADD COLUMN due_reminder_sent BOOLEAN DEFAULT FALSE;")
            conn.commit()
            print("Migration successful.")
        else:
            print("Column already exists. Skipping.")
            
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
